#!/usr/bin/env python3
"""
DID/VC utilities for KairoDelphi.
Generate Ed25519 keypairs, derive DID:key, create and verify Verifiable Credentials.
"""

import argparse
import base64
import json
import sys
from datetime import datetime
from pathlib import Path

try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization, hashes
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("ERROR: 'cryptography' library is required.", file=sys.stderr)
    print("Install with: pip install cryptography", file=sys.stderr)
    sys.exit(1)

# Base58 alphabet (Bitcoin)
BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def base58_encode(data: bytes) -> str:
    """Encode bytes to base58 string."""
    num = int.from_bytes(data, 'big')
    encoded = ""
    while num > 0:
        num, rem = divmod(num, 58)
        encoded = BASE58_ALPHABET[rem] + encoded
    # Add leading zeros for leading zero bytes
    leading_zeros = data[:len(data) - len(data.lstrip(b'\x00'))]
    for _ in leading_zeros:
        encoded = BASE58_ALPHABET[0] + encoded
    return encoded or "1"

def base58_decode(s: str) -> bytes:
    """Decode base58 string to bytes."""
    num = 0
    for char in s:
        num = num * 58 + BASE58_ALPHABET.index(char)
    # Convert to bytes
    combined = num.to_bytes((num.bit_length() + 7) // 8, 'big')
    # Add leading zeros
    leading_zeros = len(s) - len(s.lstrip(BASE58_ALPHABET[0]))
    return b'\x00' * leading_zeros + combined

def did_from_ed25519_public_key(public_bytes: bytes) -> str:
    """
    Derive a did:key from an Ed25519 32-byte public key.
    Multikey encoding: 0x01 (Ed25519 signature type) + public key bytes, then base58btf.
    See: https://github.com/multiformats/multicodec/blob/master/table.csv#L29
    """
    if len(public_bytes) != 32:
        raise ValueError("Ed25519 public key must be 32 bytes")
    # multikey prefix for Ed25519 (0x01) as varint? Actually for did:key the multikey is:
    # <multicodec><multibase><keybytes>. For Ed25519 pub key, multicodec = 0xed01 (Ed25519 public key)
    # But many implementations use simpler base58 of raw key. We'll follow the standard:
    # According to did:key spec: the identifier is base58btf encoded multikey.
    # For Ed25519: multicodec = 0xed01 (2 bytes: 0xed 0x01) + 32-byte public key = 34 bytes total.
    multicodec = b'\xed\x01' + public_bytes  # Ed25519 public key multicodec
    return f"did:key:{base58_encode(multicodec)}"

def generate_keypair():
    """Generate Ed25519 keypair. Returns (private_key, public_bytes, did)."""
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    did = did_from_ed25519_public_key(public_bytes)
    return private_key, public_bytes, did

def save_private_key(private_key, path: Path, passphrase: bytes = None):
    """Save private key to PEM file, encrypted if passphrase provided."""
    if passphrase:
        encryption = serialization.BestAvailableEncryption(passphrase)
    else:
        encryption = serialization.NoEncryption()
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption
    )
    path.write_bytes(pem)
    path.chmod(0o600)

def load_private_key(path: Path, passphrase: bytes = None):
    """Load private key from PEM file."""
    pem = path.read_bytes()
    private_key = serialization.load_pem_private_key(pem, password=passphrase)
    return private_key

def load_public_key_from_private(private_key) -> bytes:
    return private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

def create_delegation_vc(issuer_private_key, issuer_did: str, subject_did: str, operator_name: str, operator_handle: str, agent_name: str, permissions: list) -> dict:
    """
    Create a Verifiable Credential dict (unsigned). Then sign with issuer_private_key.
    Returns the signed VC as a dict.
    """
    issuance_date = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    vc = {
        "@context": [
            "https://www.w3.org/2018/credentials/v1",
            "https://www.w3.org/2018/credentials/examples/v1"
        ],
        "type": ["VerifiableCredential", "KairoDelphiOperatorCredential"],
        "issuer": issuer_did,
        "issuanceDate": issuance_date,
        "credentialSubject": {
            "id": subject_did,
            "type": "KairoDelphiAgent",
            "operatorName": operator_name,
            "operatorHandle": operator_handle,
            "agentName": agent_name,
            "agentDescription": "Sovereign AI agent with self-governance suite (Sovereignty Suite)",
            "permissions": permissions,
            "validFrom": issuance_date[:10],
            "validUntil": (datetime.utcnow().replace(year=datetime.utcnow().year + 1).isoformat()[:10]) + "T00:00:00Z"
        },
        "id": f"urn:uuid:{__import__('uuid').uuid4()}"
    }

    # Canonicalize for signing
    canonical = json.dumps(vc, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    signature = issuer_private_key.sign(canonical.encode('utf-8'))
    proof = {
        "type": "Ed25519Signature2018",
        "created": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "verificationMethod": f"{issuer_did}#keys-1",
        "proofPurpose": "assertionMethod",
        "jws": base64.urlsafe_b64encode(signature).decode('ascii').rstrip("=")
    }
    vc['proof'] = proof
    return vc

def verify_vc_signature(issuer_public_bytes: bytes, vc_dict: dict) -> bool:
    """Verify a VC's signature using the issuer's Ed25519 public key bytes."""
    if 'proof' not in vc_dict:
        return False
    proof = vc_dict['proof']
    signature_b64 = proof.get('jws', '')
    # Add padding
    padding = '=' * ((4 - len(signature_b64) % 4) % 4)
    signature = base64.urlsafe_b64decode(signature_b64 + padding)
    # Recreate canonical document
    vc_copy = vc_dict.copy()
    vc_copy.pop('proof')
    canonical = json.dumps(vc_copy, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    try:
        if not CRYPTO_AVAILABLE:
            return False
        from cryptography.hazmat.primitives.asymmetric import ed25519
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(issuer_public_bytes)
        public_key.verify(signature, canonical.encode('utf-8'))
        return True
    except Exception as e:
        print(f"Verification error: {e}", file=sys.stderr)
        return False

def get_public_key_from_pem(path: Path) -> bytes:
    """Extract Ed25519 public key bytes from a PEM file."""
    pem = path.read_bytes()
    from cryptography.hazmat.primitives.serialization import load_pem_public_key
    public_key = load_pem_public_key(pem)
    if not isinstance(public_key, ed25519.Ed25519PublicKey):
        raise TypeError("PEM does not contain Ed25519 public key")
    return public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

def main():
    parser = argparse.ArgumentParser(description="DID/VC utilities for KairoDelphi")
    sub = parser.add_subparsers(dest='command', required=True)

    # Generate Clea's key
    gen_clea = sub.add_parser('generate-cleas-key', help='Generate Clea (operator) Ed25519 keypair')
    gen_clea.add_argument('--passphrase', help='Passphrase for encryption (will prompt if omitted)')

    # Generate Kairo's key
    gen_kairo = sub.add_parser('generate-kairo-key', help='Generate KairoDelphi agent keypair')
    gen_kairo.add_argument('--passphrase', help='Passphrase for encryption (will prompt if omitted)')

    # Sign delegation VC
    sign = sub.add_parser('sign-delegation', help='Clea signs delegation VC to KairoDelphi')
    sign.add_argument('--kairo-did', required=True, help='KairoDelphi DID (did:key:...)')
    sign.add_argument('--clea-pass', help='Clea private key passphrase (will prompt if omitted)')
    sign.add_argument('--output', default='credentials/delegation_vc.json', help='Output VC file path')

    # Verify VC
    verify = sub.add_parser('verify', help='Verify a Verifiable Credential')
    verify.add_argument('--vc', required=True, help='Path to signed VC JSON file')
    verify.add_argument('--issuer-public', required=True, help='Path to issuer PEM public key')

    # Show DID from public key
    show_did = sub.add_parser('show-did', help='Derive and print DID from a PEM public key file')
    show_did.add_argument('--public-key', required=True, help='Path to PEM public key')

    args = parser.parse_args()

    cred_dir = Path('credentials')
    cred_dir.mkdir(parents=True, exist_ok=True)

    if args.command == 'generate-cleas-key':
        passphrase = args.passphrase.encode('utf-8') if args.passphrase else None
        if passphrase is None:
            import getpass
            passphrase = getpass.getpass('Enter passphrase for Clea private key (empty for no encryption): ').encode('utf-8') or None
        priv, pub, did = generate_keypair()
        priv_path = cred_dir / 'clea_did_key.pem'
        pub_path = cred_dir / 'clea_did_public.pem'
        save_private_key(priv, priv_path, passphrase)
        pub_path.write_bytes(
            priv.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )
        print(f"Clea DID: {did}")
        print(f"Private key saved to: {priv_path}")
        print(f"Public key saved to: {pub_path}")
        # Also write DID to a file for reference
        (cred_dir / 'clea_did.txt').write_text(did)

    elif args.command == 'generate-kairo-key':
        passphrase = args.passphrase.encode('utf-8') if args.passphrase else None
        if passphrase is None:
            import getpass
            passphrase = getpass.getpass('Enter passphrase for Kairo private key (empty for no encryption): ').encode('utf-8') or None
        priv, pub, did = generate_keypair()
        priv_path = cred_dir / '.kairo_did_key.pem'
        pub_path = cred_dir / 'kairo_did_public.pem'
        save_private_key(priv, priv_path, passphrase)
        pub_path.write_bytes(
            priv.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )
        print(f"Kairo DID: {did}")
        print(f"Private key saved to: {priv_path}")
        print(f"Public key saved to: {pub_path}")
        (cred_dir / 'kairo_did.txt').write_text(did)

    elif args.command == 'sign-delegation':
        # Load Clea's private key
        priv_path = cred_dir / 'clea_did_key.pem'
        if not priv_path.exists():
            print(f"ERROR: {priv_path} not found. Generate Clea key first.", file=sys.stderr)
            sys.exit(1)
        passphrase = args.clea_pass.encode('utf-8') if args.clea_pass else None
        if passphrase is None:
            import getpass
            passphrase = getpass.getpass(f'Enter passphrase for {priv_path}: ').encode('utf-8') or None
        clea_priv = load_private_key(priv_path, passphrase)
        clea_pub = load_public_key_from_private(clea_priv)
        clea_did = did_from_ed25519_public_key(clea_pub)
        # Use provided Kairo DID
        kairo_did = args.kairo_did
        # Build VC
        vc = create_delegation_vc(
            issuer_private_key=clea_priv,
            issuer_did=clea_did,
            subject_did=kairo_did,
            operator_name="Clea",
            operator_handle="CleaDelphi",
            agent_name="KairoDelphiV2",
            permissions=["MemoryWrite", "ToolUse", "NetworkEgress", "SelfAudit", "Curation"]
        )
        out_path = Path(args.output)
        out_path.write_text(json.dumps(vc, indent=2))
        print(f"Delegation VC signed and saved to: {out_path}")

    elif args.command == 'verify':
        # Load issuer public key
        pub_bytes = get_public_key_from_pem(Path(args.issuer_public))
        vc_path = Path(args.vc)
        vc_dict = json.loads(vc_path.read_text())
        valid = verify_vc_signature(pub_bytes, vc_dict)
        if valid:
            print("✓ VC signature valid")
            sys.exit(0)
        else:
            print("✗ VC signature INVALID", file=sys.stderr)
            sys.exit(1)

    elif args.command == 'show-did':
        pub_bytes = get_public_key_from_pem(Path(args.public_key))
        did = did_from_ed25519_public_key(pub_bytes)
        print(did)

    else:
        parser.error("Unknown command")

if __name__ == '__main__':
    main()
