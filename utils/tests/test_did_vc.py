#!/usr/bin/env python3
"""Unit tests for utils.did_vc"""

import sys
import json
import tempfile
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'utils'))

from did_vc import (
    generate_keypair, did_from_ed25519_public_key,
    create_delegation_vc, verify_vc_signature,
    base58_encode, base58_decode
)

def test_base58_roundtrip():
    data = b"hello world"
    enc = base58_encode(data)
    dec = base58_decode(enc)
    assert dec == data, "base58 roundtrip failed"
    print("✓ base58 roundtrip OK")

def test_keypair_generation():
    priv, pub, did = generate_keypair()
    assert pub is not None and len(pub) == 32
    assert did.startswith("did:key:")
    print(f"✓ keypair generation OK (DID: {did})")

def test_vc_sign_and_verify():
    # Generate two keypairs: issuer (Clea) and subject (Kairo)
    issuer_priv, issuer_pub, issuer_did = generate_keypair()
    _, _, subject_did = generate_keypair()
    vc = create_delegation_vc(
        issuer_private_key=issuer_priv,
        issuer_did=issuer_did,
        subject_did=subject_did,
        operator_name="Clea",
        operator_handle="CleaDelphi",
        agent_name="KairoDelphiV2",
        permissions=["MemoryWrite", "ToolUse"]
    )
    assert 'proof' in vc
    # Verify with issuer public key
    issuer_pub_bytes = issuer_pub
    valid = verify_vc_signature(issuer_pub_bytes, vc)
    assert valid, "Signature verification failed"
    print("✓ VC sign + verify OK")

def test_vc_tampering_detection():
    issuer_priv, issuer_pub, issuer_did = generate_keypair()
    _, _, subject_did = generate_keypair()
    vc = create_delegation_vc(
        issuer_private_key=issuer_priv,
        issuer_did=issuer_did,
        subject_did=subject_did,
        operator_name="Clea",
        operator_handle="CleaDelphi",
        agent_name="KairoDelphiV2",
        permissions=["MemoryWrite"]
    )
    # Tamper
    vc_copy = vc.copy()
    vc_copy['credentialSubject']['operatorName'] = "Eve"
    valid = verify_vc_signature(issuer_pub, vc_copy)
    assert not valid, "Tampering not detected!"
    print("✓ Tampering detection OK")

def test_pem_roundtrip():
    from did_vc import save_private_key, load_private_key
    priv, _, _ = generate_keypair()
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "test_key.pem"
        save_private_key(priv, path, passphrase=b"testpass")
        loaded = load_private_key(path, passphrase=b"testpass")
        # Compare by signing same message
        msg1 = b"test"
        sig1 = priv.sign(msg1)
        msg2 = b"test"
        sig2 = loaded.sign(msg2)
        # They are different keys? Actually they are the same key reloaded; signatures should verify
        from cryptography.hazmat.primitives.asymmetric import ed25519
        pub = priv.public_key()
        pub.verify(sig1, msg1)
        pub.verify(sig2, msg2)
    print("✓ PEM encrypt/decrypt roundtrip OK")

if __name__ == '__main__':
    print("Running DID/VC unit tests...")
    test_base58_roundtrip()
    test_keypair_generation()
    test_vc_sign_and_verify()
    test_vc_tampering_detection()
    test_pem_roundtrip()
    print("\nAll tests passed! 🧿🔐")
