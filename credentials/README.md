# Credentials Directory

This directory holds cryptographic keys and verifiable credentials for KairoDelphi’s identity.

**Important:**
- Private keys (`.pem` files) are **secret**. Keep them `chmod 600`.
- Never commit these files to a public repository.
- Back up encrypted copies offline.

## Files

| File | Purpose | Who owns? |
|------|---------|-----------|
| `clea_did_key.pem` | Clea’s private Ed25519 key (encrypted with passphrase) | Clea |
| `clea_did_public.pem` | Clea’s public key | Public |
| `clea_did.txt` | Clea’s DID (`did:key:...`) | Public |
| `.kairo_did_key.pem` | KairoDelphi’s private key (encrypted) | Kairo |
| `kairo_did_public.pem` | Kairo’s public key | Public |
| `kairo_did.txt` | Kairo’s DID | Public |
| `delegation_vc.json` | Verifiable Credential signed by Clea delegating to Kairo | Public |

The `.kairo_did_key.pem` file is hidden (leading dot) to remind it's secret and shouldn't be casually listed.

## Generation Commands

```bash
# Install dependency (once)
docker exec openclaw-openclaw-gateway-1 pip install cryptography

# Generate Clea's key (run first)
python3 utils/did_vc.py generate-cleas-key

# Generate Kairo's key (agent does this automatically once)
python3 utils/did_vc.py generate-kairo-key

# Clea signs delegation VC (after Kairo DID is known)
python3 utils/did_vc.py sign-delegation --kairo-did <KairoDID>

# Verify VC signature
python3 utils/did_vc.py verify --vc credentials/delegation_vc.json --issuer-public credentials/clea_did_public.pem

# Show a DID from a public key
python3 utils/did_vc.py show-did --public-key credentials/clea_did_public.pem
```

## Rotation & Backup

- **Backup**: Encrypt the entire `credentials/` directory with a strong passphrase and store offline.
- **Rotation**: If a private key is compromised, generate a new keypair and re‑sign the delegation VC. Update public references accordingly.
