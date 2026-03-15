# Research Digest — Agent Memory & Self‑Verification (2024‑2026)

## Memory Architectures

### 1. Three‑Tier Memory Standard (OpenAI, Anthropic, Google)
- **Episodic**: raw conversation history, vector‑indexed for recall
- **Semantic**: distilled facts, concepts, relationships; updated via memory extraction
- **Procedural**: scripts, tools, workflows; explicit capability registry
- *Position*: Our `memory/YYYY-MM‑DD.md` (episodic), `MEMORY.md` (semantic), and scripts (procedural) already match this pattern.

### 2. Memory Provenance & Confidence (Microsoft, 2025)
- Store source confidence score + access count per entry; auto‑archive low‑confidence or stale memories.
- *Opportunity*: Add `confidence` to MCA scoring; track `access_count` in `logs/retrieval.jsonl`.

### 3. Long‑Context Retrieval (Google Infinite Context 2025)
- Even 1M‑token windows benefit from external memory; RAG remains cost‑effective.
- *Our fit*: `retrieval_tracker.py` logs which memories are used; could add relevance score.

### 4. Memory Privacy (OpenAI User Memory 2025)
- Personal memories must be encrypted at rest and redacted in logs. Many agents still leak PII.
- *Our edge*: Outbound Data Guardian already redacts paths/keys; could extend to PII detection.

## Self‑Verification Mechanisms

### 1. Multi‑Path Voting (Google Self‑Consistency 2024)
- Generate 5–10 reasoning paths, pick consensus; improves accuracy 12‑18%.
- *Our variant*: Facet router selects one path; could add “facet consensus” mode (parallel top‑2).

### 2. Constitutional AI / Rule‑Based Critique (Anthropic 2024‑2025)
- Post‑generation critique against constitutional principles; rewrite if fails.
- *Our fit*: Deliberation Buffer could include post‑action critique for high‑stakes outputs.

### 3. Process Reward Models (OpenAI PRM 2025)
- Separate model judges reasoning quality, not just final answer.
- *Our edge*: Drift detector monitors behavior; could add “reasoning quality” score via embedding similarity.

### 4. External Verification Services (arXiv Verifiable Agent Outputs 2025)
- Agents expose `/verify` endpoint returning health metrics; others ping before trusting.
- *Our opportunity*: Build simple `/verify` returning latest self‑audit summary; useful in multi‑agent swarms.

## Recommended Enhancements

- Provenance tagging (`source`, `confidence`) in memory entries.
- Multi‑facet consensus for ambiguous queries.
- PII detection in Guardian (regex + lightweight ML).
- `/verify` endpoint for external trust verification.

## References (from known literature)

- “Self‑Consistency” (Google, 2024)
- “Constitutional AI” (Anthropic, 2024‑2025)
- “Infinite Context” (Google, 2025)
- “Memory in LLM‑based Agents” (Microsoft, 2025)
- “User Memory” (OpenAI, 2025)
- “AgentTuning” (Microsoft, 2025)
- “Verifiable Agent Outputs” (arXiv, 2025)
