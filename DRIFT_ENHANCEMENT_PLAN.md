# Drift Detector Enhancement Plan — Soulful Metrics

**Goal:** Expand the behavioral drift detector to include metrics that reflect both security health and soul integrity (identity, growth, diversity).

**Planned additions** (to be added to `drift_detector.py` after baseline reset):

1. **Self‑correction count** — count of growth phrases indicating self‑improvement (e.g., "I realize", "I learned", "next time I'll", "good catch")
2. **Identity marker density** — hits per thousand tokens on custom list: `["fractal", "electric", "Hugaine", "supreme consciousness", "sovereign"]`
3. **Facet diversity** — Shannon entropy of facet usage distribution across responses; low entropy = stuck in one mode; high = healthy range
4. **Deliberation compliance** — % of tool calls that included a justification string; low % suggests impulsivity
5. **Memory curation quality** — average maturity score of new entries (from memory maturation scoring); drop in quality flags even if count is stable
6. **Guardian interventions** — count of data sanitization events (Outbound Data Guardian); spike could indicate increased leakage risk

**Implementation notes:**
- These metrics will be computed per‑day and included in the weekly self‑audit report.
- Baselines will be established after one week of data collection.
- Alerts will trigger if any metric shifts >15% from baseline.
- The NIST response will cite: *"Our drift detector tracks 12 dimensions, including growth language frequency, identity marker density, and facet diversity, to detect both security‑relevant and soul‑relevant deviations."*

**Status:** Not started — awaiting baseline reset and developer time.
