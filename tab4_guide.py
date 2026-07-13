# FILE NAME: tab4_guide.py

import streamlit as st

def render():
    st.subheader("📘 Sizing Guide & Formula Reference")
    st.caption("A quick reference for new/junior engineers on how each level is derived in this calculator, and the guidelines behind it. Formulas here are generic — Tab 2 shows the same formulas substituted with this tank's actual numbers.")
    
    with st.expander("🏗️ 1. Tank Level Nomenclature — what each level means", expanded=True):
        st.markdown("""
| Level | Full Name | Engineering Purpose |
|---|---|---|
| **LLLL** | Low Low Liquid Level | Pump trip / shutdown level. Protects the outlet pump from vortexing and running dry. |
| **LLL** | Low Liquid Level | Low-level alarm. Gives the operator time to react before the pump trips at LLLL. |
| **HLL** | High Liquid Level | High-level alarm. Marks the top of the usable working volume. |
| **HHLL** | High High Liquid Level | High-high trip / shutdown level. Stops the inlet before the tank overflows. |
| **Tank Top** | Shell Top / Roof | Physical top of the shell — includes freeboard for vapor space, thermal expansion, or overflow. |
        """)
        st.markdown("""
* **Hb** (LLLL→LLL) and **Ht** (HLL→HHLL) are *operator response margins* — buffer heights so a human/DCS has time to act.
* **Hw** (LLL→HLL) is the *working volume* — the only liquid that's actually "usable" in normal operation.
* **H1** (bottom→LLLL) and **H2** (HHLL→top) are *dead* and *free* volumes respectively — never used for storage, but required for safety and instrumentation.
        """)
        
    with st.expander("📏 2. Tank Diameter & Area"):
        st.latex(r"D = \left(\frac{4 \cdot V_{working}}{\pi \cdot 1.2}\right)^{1/3}")
        st.markdown("""
- An **H/D (Height/Diameter) ratio of 1.2** is assumed as a practical starting proportion for vertical storage tanks — it's a sizing seed, not a code requirement.
- Diameter is rounded per project practice; Area = π × (D/2)².
- **Guideline:** always sanity-check the resulting diameter/height against plot-plan space and foundation constraints — this formula only balances volume, not layout.
        """)
        
    with st.expander("🔩 3. LLLL — Nozzle Sizing & Anti-Vortex Margin"):
        st.latex(r"d_{calc} = \sqrt{\frac{4 \cdot Q}{\pi \cdot V}}")
        st.markdown("""
- **Q** = maximum emptying volumetric flow (m³/s), **V** = emptying velocity, **mandatorily fixed at 0.5 m/s** in this calculator as a conservative erosional-velocity limit for pump suction lines.
- The calculated ID is rounded **up** to the next standard nozzle size.
        """)
        st.latex(r"LLLL = C + R + M")
        st.markdown("""
- **C** — nozzle centerline elevation off the tank bottom (from the standard elevation table for the selected nozzle size).
- **R** — nozzle radius (D/2).
- **M** — anti-vortex margin = **max(150 mm, nozzle diameter)** — keeps the liquid surface high enough above the nozzle to prevent vortexing/air entrainment into the pump suction.
- **Guideline:** the calculated LLLL is a *minimum*. It's fine to round up further, but never go below it — and always compare against the project's Shell DEP (or equivalent) minimum, shown alongside as a reference.
        """)
        
    with st.expander("⏱️ 4. LLL & HHLL — Operator Response Margins"):
        st.latex(r"\Delta H = \frac{Flow \times Time}{Area \times 60} \times 1000\ \text{(mm)}")
        st.markdown("""
- Same formula for both directions — **emptying** flow & time gives the **LLL margin** (above LLLL); **filling** flow & time gives the **HHLL margin** (below the top).
- Margin used = **max(150 mm, ΔH)** — 150 mm is treated as an absolute practical minimum even if the flow/time math gives a smaller number.
- **Guideline:** Response time is normally **5–15 minutes**, reflecting realistic operator/DCS reaction time. Shorter times need faster automated trips; longer times need a taller tank — flag this trade-off to your lead if the client hasn't specified one.
        """)
        
    with st.expander("📦 5. HLL — Working Height"):
        st.latex(r"H_{working} = \frac{V_{working}}{Area} \times 1000\ \text{(mm)}")
        st.markdown("""
- Directly converts the required working **volume** into a **height**, using the tank's cross-sectional area.
- HLL = LLL + this working height.
        """)
        
    with st.expander("🛡️ 6. Tank Top — Freeboard / Overflow Margin"):
        st.markdown("**Option A — No overflow nozzle:**")
        st.latex(r"Margin = \max\left(300\ \text{mm},\ HHLL \times \frac{0.05}{0.95}\right)")
        st.markdown("""
- This enforces the "**HHLL ≤ 95% of total height**" rule — the tank always keeps at least 5% freeboard above the trip level, covering thermal expansion of the liquid and any transient overshoot.
- 300 mm is the absolute floor regardless of what the 95% rule gives.
        """)
        st.markdown("**Option B — With overflow nozzle (self-venting):**")
        st.latex(r"Margin = \max(300\ \text{mm},\ 1.5D + 150\ \text{mm})")
        st.latex(r"F_r = \frac{V}{\sqrt{g \cdot D}} < 0.3\ \text{for self-venting flow}")
        st.markdown("""
- The overflow nozzle itself is sized off max fill rate so the overflow can gravity-drain **without surging back up the pipe** (Froude number check).
- **Guideline:** an overflow nozzle is a passive safety device, not a substitute for the HHLL trip — it's the last line of defense, so don't undersize it to save on margin.
        """)
        
    with st.expander("🌬️ 7. Roof Type & TVP (True Vapor Pressure) Rules"):
        st.markdown("""
**API 650 (atmospheric tanks):**
- TVP ≤ 10 kPaa → Fixed Roof is safe and most economical.
- TVP > 10 kPaa → Fixed Roof is **not allowed** (vapor emissions) — a Floating Roof is required.
- TVP > 75 kPaa → outside API 650's scope entirely — move to a **pressure vessel (ASME)**.
**API 620 (low-pressure gas-tight tanks):**
- Suitable up to 75 kPaa with a gas-tight Fixed Dome Roof.
- TVP > 75 kPaa → move to a **pressure vessel (ASME Section VIII)**.
**Guideline:** TVP should be evaluated at the *maximum expected storage/ambient temperature*, not just the normal operating temperature — an undersized roof choice here is a common junior-engineer mistake.
        """)
        
    with st.expander("✅ 8. General Notes for Junior Engineers"):
        st.markdown("""
- **Everything with a "Formula suggestion" tooltip in Tab 1 is a calculated minimum/starting point** — you can round up, but check with your lead before rounding down.
- **Shell DEP references are informational only** in this tool — always confirm against the actual project specification, which may be more stringent.
- **The 0.5 m/s emptying velocity is fixed by design intent in this calculator** — if your project basis differs, flag it rather than overriding the number silently.
- Cross-check the final diameter/height against available plot space, wind/seismic loading, and foundation design early — sizing here is volumetric only.
- Use **Tab 2** to trace every number back to its formula before issuing the calc for review — that traceability is what a reviewer will check first.
        """)