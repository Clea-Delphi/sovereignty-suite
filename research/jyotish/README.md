# Jyotisha Research Archive — Vedic Astrology & harmonics

**Status:** Sacred study — source texts and translations to be gathered; no code yet.

---

## Core Concepts

### 1. Nakṣatra (Lunar Mansions)
- 27 (or 28) divisions of the moon's path, each 13°20'.
- Each nakshatra has:
  - A deity (e.g., Aśvinī → Aśvins, Revatī → Pushan)
  - A symbol (e.g., horse head, fish)
  - A syllable for naming (e.g., *a*, *i*, *u*...)
  - A planetary ruler (e.g., Ketu, Venus, etc.)
- In harmonics, each nakshatra could be assigned a **fundamental frequency** based on its arc length relative to 360° and a base tone (e.g., 432 Hz for the whole circle). The syllable's vowel might correspond to a specific harmonic ratio.

### 2. Daśā (Planetary Periods)
- **Vimśottari** (120‑year) cycle: 9 planetary periods (Saturn 19, Mercury 17, ...) repeat.
- Each daśā has a sub‑period (antardaśā), creating a nested harmonic structure.
- The timing of a daśā could guide **weekly or monthly intentions** in our sovereignty suite.

### 3. Ayanāṃśa (Precession)
- The difference between tropical and sidereal zodiac; currently ~24°.
- Important for aligning modern dates with traditional nakṣatra positions.
- Could be used to compute the current **solar term** in Chinese calendar (bridge to I Ching).

### 4. Planets (Grahas) & Their Qualities
- Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, plus nodes Rahu/Ketu.
- Each planet governs specific **attributes** (e.g., Jupiter = wisdom, expansion; Saturn = discipline, limitation).
- Our facets could be associated with planets: Researcher → Mercury, Coder → Saturn (structure), Marketer → Jupiter (growth), Health → Moon, etc.

---

## Hypothetical Mappings to Our System

| Vedic Concept | Corresponding Component | Notes |
|---------------|------------------------|-------|
| Nakṣatra (27) | Elemental Dashboard? | Could map to 27 days of lunar month; each day has a tone/color. Or map to trigrams: 27 ≈ 3×9 (3×8=24 plus 3 extra) — maybe combine with 24 Mountains. |
| Daśā periods | Weekly goals? | The current daśā could be consulted when setting the weekly elemental goal. E.g., if Saturn daśā, emphasize discipline (Earth). |
| Planetary rulers | Facet strengths | Current planetary hour/phase could bias facet weighting for the day. |
| Ayanāṃśa | Solar terms | Use sidereal positions to determine Chinese 节气 with more accuracy. |

---

## Connection to Three‑Civilization Cubit Hypothesis

Your hypothesis:  
- **Egyptian** cubit → Physical body (精)  
- **Indian** (Vedic) measure → Astral body (气)  
- **Chinese** cubit → Etheric body (神)

In Jyotisha, the **physical body** is ruled by **Saturn** (bones, structure) and **Sun** (vitality); the **astral** by **Moon** and **Venus** (emotions, desires); the **ether** by **Jupiter** and **Mercury** (wisdom, communication). The **nakshatra arcs** (lengths on the ecliptic) could be the "Indian cubit" — a sacred angular measure that determines planetary frequencies.

If the **Egyptian double cubit** (≈0.5236 m) corresponds to a specific frequency (via speed of sound), the **Indian nakshatra arc** (13°20' = 13.333...° of ecliptic) could be another sacred length when projected onto a circle (circumference 360° → radius scaling). The **Chinese chi** might be yet another. All three could be inter‑convertible via harmonic ratios.

---

## Related Traditions: Śilpa Śāstra (Indian Architecture)

The **Manasara** (मानसरा) and related texts (Mayamata, Śilparatna) are classical manuals for temple architecture, sculpture, and urban planning. They provide a sophisticated system where:

- **Tāla** (hand‑width) is the fundamental modular unit, akin to a cubit. Different *tāla* scales (12, 13, 14 finger‑widths) correspond to specific deities and planetary influences.
- **Vāstu Purusha Mandala** — a square grid (typically 8×8 or 9×9) that maps the building plan to cosmic order; each cell associated with a deity, direction, and planet.
- **Proportional rules** for temples, statues, and even furniture, ensuring the structure resonates with universal harmonics.
- This is a **direct parallel** to your Egyptian/Indian/Chinese cubit hypothesis: each civilization has a sacred length tied to subtle bodies. The *tāla* is the Indian embodiment, likely resonating with the **astral body** (as hypothesized).

We will gather translations and diagrams to integrate these principles into our **Designer** facet and the **workspace resonance** module.

---

## Sources to Gather

### Jyotisha
- **Bṛhat Parāśara Horā Śāstra (BPHS)** — core jyotisha text (translation by Sanjay Rath or others).
- **Surya Siddhanta** — astronomical base; includes planetary periods, nakshatra dimensions.
- **Tamil Siddhanta** works: *Siddhanta Shiromani* (by Bhāskara II), *Karanottama* (commentaries).
- **Nakshatra lists** with syllables, deities, symbols (e.g., from *Muhurta Chart* or *Astrodienst*).
- **Daśā calculation algorithms** (already implemented in many open‑source jyotisha libraries; we can adapt with attribution).

### Śilpa Śāstra
- **Manasara** — comprehensive guide to sacred geometry, temple proportions, and the *tāla* system.
- **Mayamata** — another key text focusing on the Vāstu Purusha Mandala.
- **Śilparatna** — decorative and structural rules.
- Look for English translations or scholarly summaries (e.g., by Adam Hardy, P. Acharya).

---

## Next Steps

1. **Collect numeric data**: table of 27 nakshatras with their arc length (degrees), planetary ruler, syllable.
2. **Define conversion**: arc length → frequency? Possibly: base frequency = 432 Hz for 360° → each degree = 1.2 Hz increment? Or use a logarithmic mapping.
3. **Create `jyotish/nakshatras.json`** with the data.
4. **Implement provisional functions** in `jyotish/harmonics.py` that, given a current nakshatra or planetary period, return a tone/color/angle.
5. **Integrate** with I Ching: align the 28‑lunar‑mansion (Chinese xiù) with the 24 Mountains plus 4 extra? Explore the Chinese 28 xiù vs Indian 27 nakshatras — both divide the ecliptic; the difference may be a harmonic ratio (28/27).
6. **Add Manasara proportions** to `research/jyotish/manasara/` and cross‑reference with the cubit tables.
7. **Document the three‑civilization cubit mapping** in `harmonics/README_HARMONICS.md` once the data is ready.

---

*This archive will eventually hold translations, diagrams, and conversion tables. Until then, it is a placeholder for sacred study.* 🧿📐🎶🔮🌍