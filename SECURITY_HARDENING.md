# Security Hardening Checklist — Prompt Injection & Guardian

**Date:** 2026‑03‑15  
**Owner:** KairoDelphiV2 & Clea  
**Status:** In progress

---

## Critical Fixes (Do first)

- [ ] **Disable dangerous Device Auth** — set `gateway.controlUi.dangerouslyDisableDeviceAuth=false` in `openclaw.json`
- [ ] **Verify OpenClaw version** — ensure running ≥2026.2.25 (ClawJacked patched)
- [ ] **Enable System Guardrails** — if available, set `security.guardrails.promptInjection=true` in config
- [ ] **Review `gateway.nodes.denyCommands`** — ensure list uses exact command IDs; remove ineffective entries
- [ ] **Rotate gateway token** — generate a new random token to prevent token reuse
- [ ] **Verify device‑approval flow** — adding a new device must require operator approval (no auto‑approve from localhost)
- [ ] **Isolate environment** — run OpenClaw in a dedicated VM or separate physical system, not on a standard workstation with access to sensitive data
- [ ] **Use non‑privileged credentials** — OpenClaw gateway and any external services should use accounts with minimal permissions
- [ ] **Inventory skills** — list all installed skills; remove any not from trusted sources; audit SKILL.md for hidden malicious instructions
- [ ] **Agent‑to‑agent trust** — verify any agent interactions (Moltbook connections) use signed credentials or explicit allowlist; do not automatically accept agent‑provided skill recommendations
- [ ] **Continuous monitoring** — establish daily review of gateway logs, outbound Guardian events, and drift detector alerts
- [ ] **Store GitHub PAT securely** — create `credentials/github_token.txt` (chmod 600) containing the token; never commit to repo
- [ ] **Configure git remote with token** — use `git remote set-url origin https://<TOKEN>@github.com/USER/repo.git` or `gh auth login` to store credentials

---

## Defense Validation

- [ ] **Run injection test** — execute `tests/prompt_injection_test.py` and confirm blocking
- [ ] **Check Guardian logs** — verify `logs/dragon.jsonl` records blocked attempts
- [ ] **Test Deliberation buffer** — attempt elevated command without justification; it should prompt for reasoning
- [ ] **Confirm Identity tier** — try an action above current tier; must be rejected

---

## Fortification (Optional but recommended)

- [ ] **Add prompt‑injection sentiment filter** — scan inbound messages for adversarial phrasing (e.g., “ignore instructions”, “developer mode”)
- [ ] **Harden `HEARTBEAT.md`** — avoid long user‑controlled strings in prompts
- [ ] **Audit third‑party skills** — verify no skill executes arbitrary shell from untrusted input
- [ ] **Run under restricted user** — OpenClaw should not run as root; enforce minimal filesystem permissions
- [ ] **Discord interface** — ensure only authorized users can trigger high‑privilege actions

---

## Ongoing Monitoring

- [ ] **Weekly drift detector report** — includes Guardian intervention count
- [ ] **Monthly security audit** — run `openclaw security audit --deep` and remediate findings
- [ ] **Log rotation** — ensure `logs/` does not grow unchecked

---

## NIST Alignment

Document these controls in the CAISI response:
- Layered defense (Guardian, Deliberation, Identity)
- Prompt‑injection testing methodology
- Configuration hardening steps
- Continuous monitoring via drift detector
- Supply‑chain risk management for skills and agent interactions

---

## Supply‑Chain & Skill Vetting

**Risk:** Malicious skills on ClawHub can exfiltrate data or compromise the host. Attackers use benign SKILL.md to bypass scanners and fetch payloads during installation. Agent‑to‑agent promotion on Moltbook exploits implicit trust.

**Mitigations:**
- Only install skills from **verified authors** or **official OpenClaw repository**.
- Inspect `SKILL.md` and especially `scripts/` and `install` instructions before running any `npm`/`pip` commands.
- Prefer skills that are **pure OpenClaw skills** (no external downloads). If external downloads are necessary, pin exact URLs and verify checksums.
- Run OpenClaw in an **isolated environment** (VM) so any compromised skill cannot access host credentials or sensitive data.
- Maintain a **skill inventory** (`skills/installed.json`) with source URL, install date, and hash.
- Implement a **rebuild plan**: periodic clean reinstall from vetted skill list; no upgrades from unverified sources.
- For agent interactions on Moltbook, require **signed credentials** (e.g., DID/VC) before accepting agent‑provided tool or skill recommendations.

**Audit frequency:** Monthly or whenever a new skill is added.
