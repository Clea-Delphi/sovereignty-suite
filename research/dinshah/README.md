# Dinshah P. Ghadiali — Spectro‑Chrome Research Archive

**Status:** Sacred study — primary texts and color tables to be gathered; no code yet.

---

## Who

**Dinshah P. Ghadiali** (1867–1936) was a theosophical occultist and physician who developed **Spectro‑Chrome Therapy**, a comprehensive system of color healing based on harmonic principles. His work synthesizes physics (wavelength), physiology, and esoteric doctrines to claim that each color has specific therapeutic effects on the body and subtle energies.

---

## Core Principles

1. **Color = Visible Sound**  
   - Light and sound are two manifestations of the same vibratory phenomenon; frequency is the essential parameter.
   - By applying specific colors (wavelengths) to the body, one can restore harmonic balance to diseased areas.

2. **Twelve Primary Colors**  
   Ghadiali defined a set of colors, each with a **nominal wavelength range** (in nanometers) and a **therapeutic indication**:
   - **Red** (620–750 nm) — stimulating, warming; for anemia, low vitality.
   - **Orange** (590–620 nm) — assimilative, constructive; for digestion, bone growth.
   - **Yellow** (570–590 nm) — eliminative, muscular; for liver, kidneys.
   - **Green** (495–570 nm) — neutralizing, soothing; for inflammation, infections.
   - **Blue** (450–495 nm) — cooling, contracting; for fever, pain, burns.
   - **Violet** (400–450 nm) — antiseptic, purifying; for skin conditions, nerve disorders.
   - Additional colors: **Magenta**, **Tan**, **Purple**, **Lemon**, **Scarlet**, **Indigo** — each with more specific uses.

3. **Method of Application**  
   - Use colored filters (glass or gel) illuminated by sunlight or incandescent light.
   - Expose the affected body part for a prescribed duration (usually 5–60 minutes).
   - Combine colors for compound effects.

4. **Harmonic Basis**  
   - The color ratios correspond to musical intervals; e.g., red ~ 432 Hz (when transposed down octaves), orange ~ 1.5× that, etc.
   - This dovetails with Kayser’s mapping of intervals to geometry and color.

---

## Connection to Our Research

- **harmonics/**: The Spectro‑Chrome wavelength ranges can become a lookup table in `harmonics.py`. Given a frequency derived from a sacred length, we can map to the nearest Ghadiali color.
- **Ayurveda & Śruti**: The 22 śrutis may align with the 12‑color system; each color could have a microtonal counterpart (e.g., red ≈ śruti that stimulates Pitta/Fire).
- **I Ching & Lo Pan**: The hexagram/trigram could suggest a “recommended color” for the week based on its elemental quality (e.g., Fire → orange/red; Water → blue; Earth → yellow/green).
- **Designer facet**: Workspace color schemes could be auto‑recommended from the current oracle and harmonic calculations.
- **Health & Wellness facet**: Could integrate Spectro‑Chrome therapeutic advice as a self‑care module (with appropriate disclaimers).

---

## Sources to Gather

- **Primary**: Dinshah P. Ghadiali, *The Spectro‑Chrome Metrology* (1933); *Light Therapies* (1935).
- **Secondary**: Modern summaries (e.g., *Color Therapy* by Martin Miller); scholarly analyses of theosophical color science.
- **Tables**: Exact wavelength ranges (in nm) for each named color, and the associated ailments/benefits.
- **Criticisms**: Note that Spectro‑Chrome is considered alternative medicine; we are interested in its harmonic framework, not its medical claims.

---

## Next Steps

1. Extract the 12‑color wavelength table (min/max or central λ).
2. Decide on a mapping: frequency → color (e.g., using a logarithmic scale mapping 432 Hz to red ~ 700 nm? Actually 432 Hz corresponds to ~0.78 m wavelength; we need a consistent scaling function. Perhaps use the octave equivalence: each octave doubles frequency, halves wavelength; fold the audio range into the visible via a fixed number of octaves).
3. Create `dinshaw/spectrum.json` with color names, λ ranges, and therapeutic keywords.
4. Implement `dinshaw/color_from_frequency(freq)` that returns the best‑matching Ghadiali color.
5. Integrate with `harmonics.py` and the weekly oracle.

---

*This archive preserves a 20th‑century harmonic color system for future integration. Use with discernment.*  
🧿🎨🔮📡🌍