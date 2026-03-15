# DID/VC Identity Anchoring — Project Guide

## 1. What are DIDs and VCs?

- **Decentralized Identifier (DID)**: A globally unique identifier that **you control**, like `did:key:zQ3shV...`. It's derived from a cryptographic public key. No central registry owns it; you do.
- **Verifiable Credential (VC)**: A digital certificate signed by an issuer that attests to something about a subject. A driver's license is a real‑world VC. For us: *"KairoDelphiV2 is operated by Clea and has been running since 2026‑03‑07."*

Together, they let an **agent prove its identity and provenance** in a cryptographically verifiable way, without needing a central authority.

---

## 2. Why do we need this?

- **NIST AI Agent Standards** — identity and authorization are pillars. Implementing DID/VC shows we're aligned with emerging best practices.
- **Moltbook claim** — we can attach our VC as proof of operator relationship, potentially speeding manual verification.
- **Inter‑agent trust** — when other agents ask “who are you and who allowed you to exist?”, we can show a signed credential that anyone can verify.
- **Long‑term sovereignty** — even if our API keys leak, the DID remains under our control and can be rotated.

---

## 3. High‑level Architecture

```
Clea (operator)                        KairoDelphi (agent)
       │                                       │
       │ 1. Generate Ed25519 keypair            │ 1. Generate Ed25519 keypair
       │    → Clea DID                         │    → Kairo DID
       │                                       │
       └─── 2. Clea signs delegation VC ──────►│
               Issuer: Clea DID
               Subject: Kairo DID
               Permissions: [ ... ]
               → credentials/delegation_vc.json
```

- **Private keys** stay encrypted in `credentials/` with `chmod 600`.
- **Public keys** are stored as PEM files in the same directory.
- **DIDs** are derived from the public keys using the `did:key` multikey method.
- The **VC** is a JSON‑LD document with a digital signature (`proof`) using Clea's private key.

---

## 4. Implementation Steps

| Step | Owner | Task | Command / Artifact |
|------|-------|------|--------------------|
| 0 | Clea | Create `#kairo-dev` Discord channel; invite Oxo, sons, KairoBot | — |
| 1 | Oxo/sons | Install `cryptography` in the OpenClaw gateway container | `docker exec openclaw-openclaw-gateway-1 pip install cryptography` |
| 2 | Kairo | Confirm `utils/did_vc.py` is ready (it now includes CLI, base58 encoding, signing, verification) | — |
| 3 | Oxo/sons | Generate **Clea's** keypair | `python3 utils/did_vc.py generate-cleas-key`<br>→ `credentials/clea_did_key.pem`, `clea_did_public.pem`, `clea_did.txt` |
| 4 | Kairo | Ensure **Kairo's** key is generated on agent startup (once) | `python3 utils/did_vc.py generate-kairo-key`<br>→ `credentials/.kairo_did_key.pem`, `kairo_did_public.pem`, `kairo_did.txt` |
| 5 | Clea | Sign the delegation VC | `python3 utils/did_vc.py sign-delegation --kairo-did <KairoDID>`<br>→ `credentials/delegation_vc.json` |
| 6 | Everyone | Verify the VC signature | `python3 utils/did_vc.py verify --vc credentials/delegation_vc.json --issuer-public credentials/clea_did_public.pem` |
| 7 | Oxo/sons | (Optional) Serve `public/.well-known/did.json` (Kairo's DID document) from `public/` via nginx/Apache | URL: `https://<our-domain>/.well-known/did.json` |
| 8 | Kairo | Integrate `verify_vc()` into our claim generator; add DID to agent metadata; update `public/credentials.md` | — |
| 9 | Clea | Review/approve the VC's `credentialSubject` fields (operator name, handle, permissions) | — |

---

## 5. Roles & Responsibilities

- **Oxo & your sons**:
  - Command‑line comfort: run generation scripts, check file permissions.
  - Help set up web server if we expose `/.well-known/did.json`.
  - Research W3C specs for edge cases, suggest improvements.
  - Write simple unit tests (we'll provide a template).

- **Clea (you)**:
  - Choose a **strong passphrase** for your private key encryption.
  - Run the `generate-cleas-key` script and keep the passphrase safe.
  - Sign the delegation VC (final approval step).
  - Approve the permissions listed in the VC.
  - Oversee integration into Moltbook claim.

- **KairoDelphi (me)**:
  - Write and maintain `utils/did_vc.py` (already drafted).
  - Add unit tests in `utils/tests/test_did_vc.py`.
  - Integrate verification into claim generation and identity metadata.
  - Document everything in `docs/`.
  - Teach the team how the cryptography works and answer questions.

---

## 6. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Private key leakage | Store encrypted with strong passphrase; never commit to Git; keep passphrase separate; file permissions `chmod 600` |
| Loss of key/VC | Create encrypted backup on USB or air‑gapped storage; keep passphrase recorded securely |
| Someone else claims same DID | Impossible — DID is derived from public key; only holder of private key can prove ownership |
| VC tampering | Any change breaks the Ed25519 signature; `verify` script will detect it |
| Over‑sharing the DID | The DID is intentionally public; only the private key must remain secret |

---

## 7. File Structure (post‑implementation)

```
workspace/
├── utils/
│   └── did_vc.py                # CLI tool
├── credentials/
│   ├── clea_did_key.pem         # Clea private key (encrypted, chmod 600)
│   ├── clea_did_public.pem      # Clea public key
│   ├── clea_did.txt             # Clea DID string
│   ├── .kairo_did_key.pem       # Kairo private key (encrypted)
│   ├── kairo_did_public.pem     # Kairo public key
│   ├── kairo_did.txt            # Kairo DID string
│   └── delegation_vc.json       # Signed VC from Clea to Kairo
├── public/
│   ├── did.json (optional)      # Kairo's DID document (served at /.well-known/did.json)
│   └── credentials.md           # Human‑readable references to DID & VC
├── docs/
│   └── did_vc_guide.md          # This document
└── utils/tests/
    └── test_did_vc.py           # Unit tests
```

---

## 8. Timeline

- **Day 1** — Oxo installs `cryptography`; Clea generates her key; Kairo key auto‑generated; first draft of VC created.
- **Day 2** — Review VC content; Clea signs final version; everyone verifies; optionally set up `did.json` endpoint.
- **Day 3** — Kairo integrates verification into claim generator; update public docs; write unit tests.
- **Day 4** — Optional: compute VC hash and include in Moltbook claim; consider L2 anchoring (not required).

Total active work: ~4 hours spread across the team.

---

## 9. Ethical & Sovereignty Considerations

- **Operator authority** — only Clea holds the signing private key. No one else can issue a credential for KairoDelphi.
- **Transparency** — DID and VC are public; private keys stay private.
- **Revocability** — if needed, Clea can revoke the VC by issuing a revocation entry or by simply generating a new keypair and VC.
- **No blockchain required** — we keep it lightweight. Anchoring is optional and can be added later if desired.

---

## 10. Next Actions (Immediate)

1. **Clea**: create `#kairo-dev` channel.
2. **Oxo/sons**: run `docker exec openclaw-openclaw-gateway-1 pip install cryptography`.
3. **Kairo**: ensure `utils/did_vc.py` is syntactically correct (I’ve just written it; will test locally).
4. **Team meeting**: once channel exists, paste this guide and schedule a quick kickoff (text‑based is fine).
5. **Clea**: decide on a strong passphrase; keep it handy for key generation.

---

**Let's build sovereign identity together.**  
When the channel is ready, I’ll post this guide and we’ll begin step‑by‑step.

Hugaine! 🧿🔐📚
