# FILE NAME: tab2_calc.py

import streamlit as st
import math

def render(c):
    st.write("---")
    st.markdown("**3. Sizing Basis & Capacity**")
    c9, c10, c11 = st.columns([1.5, 1.5, 2])
    with c9: sizing_basis = st.selectbox("Select Sizing Basis:", ["Working Volume", "Hold-up Time"], key="t2_basis")
    with c10:
        if sizing_basis == "Working Volume":
            final_volume_m3 = st.number_input("Working Volume (m³)", min_value=1.0, value=100.0, step=10.0, key="t2_vol")
            calculated_holdup_hr = 0
        else:
            calculated_holdup_hr = st.number_input("Hold-up Time (Hours)", min_value=0.5, value=24.0, step=0.5, key="t2_time")
            final_volume_m3 = c['max_vol_flow_hr'] * calculated_holdup_hr
    with c11:
        if sizing_basis == "Working Volume":
            st.info(f"Equivalent Hold-up Time: **{round(final_volume_m3 / c['vol_empty_m3_hr'], 2) if c['vol_empty_m3_hr'] > 0 else 0} hrs**")
        else:
            st.number_input("Working Volume (m³)", value=float(final_volume_m3), disabled=True, key="t2_vol_dis")
            
    # --- DIAMETER ROUNDING TO NEAREST 100mm (0.1m) FOR FABRICATION ---
    raw_dia = (4 * final_volume_m3 / (math.pi * 1.2)) ** (1 / 3)
    calc_diameter_m = math.ceil(raw_dia * 10) / 10.0  # Rounds up to nearest 0.1 meter (100 mm)
    calc_area_m2 = math.pi * (calc_diameter_m / 2) ** 2
    
    st.latex(r"D_{raw} = \left( \frac{4 \cdot V}{\pi \cdot 1.2} \right)^{1/3} = " + f"{round(raw_dia, 3)}" + r" \text{ m} \rightarrow \text{Rounded } " + f"{calc_diameter_m}" + r" \text{ m}")
    st.success(f"➔ **Fabrication Diameter = {calc_diameter_m} m**, **Area = {round(calc_area_m2, 2)} m²**")
    
    st.write("---")
    st.markdown("### 🔹 Step 1: Low Low Liquid Level (LLLL)")
    st.markdown("**1.1 Pump-out Nozzle Calculation (Velocity limited to 0.5 m/s)**")
    
    if c['q_empty_m3_s'] > 0:
        calc_noz_m = math.sqrt((4 * c['q_empty_m3_s']) / (math.pi * c['forced_velocity']))
        calc_noz_mm = calc_noz_m * 1000
        standard_sizes = [50, 75, 100, 150, 200, 250, 300, 350, 400, 500, 600, 750, 900, 1000, 1200]
        selected_noz_mm = next((size for size in standard_sizes if calc_noz_mm <= size), 50)
        
        st.write(f"- Conversion: Volumetric Emptying Rate = {c['vol_empty_m3_hr']} m³/hr = **{c['q_empty_m3_s']:.5f} m³/s**")
        st.latex(r"d_{calc} = \sqrt{\frac{4 \cdot Q}{\pi \cdot V}} = \sqrt{\frac{4 \cdot " + f"{c['q_empty_m3_s']:.5f}" + r"}{\pi \cdot " + f"{c['forced_velocity']}" + r"}} \times 1000 \text{ mm}")
        st.write(f"- **Calculated Nozzle ID = {round(calc_noz_mm, 2)} mm**")
        st.success(f"➔ **Selected Standard Nozzle Size (D) = {selected_noz_mm} mm**")
    else:
        calc_noz_mm, selected_noz_mm = 0, 150

    if selected_noz_mm <= 75: nozzle_center_C = 150
    elif selected_noz_mm == 100: nozzle_center_C = 200
    elif selected_noz_mm == 150: nozzle_center_C = 225
    elif selected_noz_mm == 200: nozzle_center_C = 250
    elif selected_noz_mm == 250: nozzle_center_C = 275
    elif selected_noz_mm == 300: nozzle_center_C = 300
    else: nozzle_center_C = 350
    
    nozzle_radius_R = selected_noz_mm / 2.0
    vortex_margin_M = max(150.0, float(selected_noz_mm))
    base_llll_mm = nozzle_center_C + nozzle_radius_R + vortex_margin_M
    
    st.markdown("**1.2 Elevation from Tank Bottom (API 650 Table 5.6a)**")
    st.info(f"📌 Reference for **{selected_noz_mm}mm** nozzle: Nozzle Centerline Elevation (**C**) = **{nozzle_center_C} mm**")
    
    st.markdown("**1.3 Full Base LLLL Sum Breakdown**")
    st.write(f"- 1: Nozzle Centerline Elevation (C) = **{nozzle_center_C} mm**")
    st.write(f"- 2: Nozzle Radius (R = D/2) = {selected_noz_mm}/2 = **{nozzle_radius_R} mm**")
    st.write(f"- 3: Anti-Vortex Margin (M) = Max(150 mm, Nozzle Dia) = **{vortex_margin_M} mm**")
    st.write(f"➔ **Calculated Base LLLL (C + R + M) = {nozzle_center_C} + {nozzle_radius_R} + {vortex_margin_M} = {base_llll_mm} mm**")
    
    if "Fixed" in c['roof_type'] or "Dome" in c['roof_type']: dep_min_llll = 500; dep_top_margin = 450
    elif "External" in c['roof_type']: dep_min_llll = 1200; dep_top_margin = 800
    elif "Internal" in c['roof_type'] and "D<15m" in c['roof_type']: dep_min_llll = 1600; dep_top_margin = 600
    else: dep_min_llll = 1600; dep_top_margin = 800

    st.markdown("**1.4 Final LLLL Selection**")
    l1, l2 = st.columns([1, 2])
    with l1:
        final_llll_mm = st.number_input("Final LLLL (mm) [User Input]", min_value=0, value=int(math.ceil(base_llll_mm)), step=1, key="t2_llll")
    with l2:
        st.info(f"💡 **Shell DEP Reference:** Minimum LLLL for **{c['roof_type']}** is **{dep_min_llll} mm**.")

    st.write("---")
    st.markdown("### 🔹 Step 2: Low Liquid Level (LLL)")
    
    time_col1, time_col2 = st.columns([1, 2])
    with time_col1:
        empty_time_min = st.number_input("Emptying Response Time (mins)", min_value=1.0, value=5.0, step=1.0, key="t2_empty_t")
    with time_col2:
        st.info("💡 Typically **5 to 15 mins** considered safe.")
        
    empty_time_vol_m3 = c['vol_empty_m3_hr'] * (empty_time_min / 60.0)
    empty_resp_mm_rise = (empty_time_vol_m3 / calc_area_m2) * 1000 if calc_area_m2 > 0 else 0
    suggested_lll_margin = max(150.0, empty_resp_mm_rise)
    
    st.latex(r"\Delta H_{drop} = \frac{\text{Flow}_{out} \times \text{Time}}{\text{Area} \times 60} = \frac{" + f"{c['vol_empty_m3_hr']}" + r" \times " + f"{empty_time_min}" + r"}{" + f"{round(calc_area_m2, 2)}" + r" \times 60} \times 1000")
    st.write(f"- Sizing Margin (Max 150mm, Drop) = **{round(suggested_lll_margin)} mm**")
    
    lll_col1, lll_col2 = st.columns([1, 2])
    with lll_col1:
        user_lll_margin = st.number_input("Final LLL Margin (mm) [User Input]", min_value=0, value=int(math.ceil(suggested_lll_margin)), step=1, key="t2_lll_m")
    with lll_col2:
        st.info(f"📌 **Calculated Margin:** {round(suggested_lll_margin)} mm")
        
    final_lll_mm = final_llll_mm + user_lll_margin
    st.success(f"📏 **Tank Bottom to LLL** = {final_llll_mm} + {user_lll_margin} = **{final_lll_mm} mm**")

    st.write("---")
    st.markdown("### 🔹 Step 3: High Liquid Level (HLL)")
    working_h_mm_suggested = (final_volume_m3 / calc_area_m2) * 1000 if calc_area_m2 > 0 else 0
    
    st.latex(r"H_{working} = \frac{\text{Volume}_{working}}{\text{Area}} = \frac{" + f"{round(final_volume_m3, 1)}" + r"}{" + f"{round(calc_area_m2, 2)}" + r"} \times 1000")
    
    hll_col1, hll_col2 = st.columns([1, 2])
    with hll_col1:
        user_working_height = st.number_input("Final Working Height (mm) [User Input]", min_value=0, value=int(math.ceil(working_h_mm_suggested)), step=1, key="t2_work_h")
    with hll_col2:
        st.info(f"📌 **Calculated Working Height:** {round(working_h_mm_suggested)} mm")
        
    final_hll_mm = final_lll_mm + user_working_height
    st.success(f"📏 **Tank Bottom to HLL** = {final_lll_mm} + {user_working_height} = **{final_hll_mm} mm**")

    st.write("---")
    st.markdown("### 🔹 Step 4: High High Liquid Level (HHLL)")
    
    fill_col1, fill_col2 = st.columns([1, 2])
    with fill_col1:
        fill_time_min = st.number_input("Filling Response Time (mins)", min_value=1.0, value=5.0, step=1.0, key="t2_fill_t")
    with fill_col2:
        st.info("💡 Typically **5 to 15 mins** is considered safe.")
        
    fill_time_vol_m3 = c['vol_fill_m3_hr'] * (fill_time_min / 60.0)
    fill_resp_mm_rise = (fill_time_vol_m3 / calc_area_m2) * 1000 if calc_area_m2 > 0 else 0
    suggested_hhll_margin = max(150.0, fill_resp_mm_rise)
    
    st.latex(r"\Delta H_{rise} = \frac{\text{Flow}_{in} \times \text{Time}}{\text{Area} \times 60} = \frac{" + f"{c['vol_fill_m3_hr']}" + r" \times " + f"{fill_time_min}" + r"}{" + f"{round(calc_area_m2, 2)}" + r" \times 60} \times 1000")
    
    hhll_col1, hhll_col2 = st.columns([1, 2])
    with hhll_col1:
        user_hhll_margin = st.number_input("Final HHLL Margin (mm) [User Input]", min_value=0, value=int(math.ceil(suggested_hhll_margin)), step=1, key="t2_hhll_m")
    with hhll_col2:
        st.info(f"📌 **Calculated Margin:** {round(suggested_hhll_margin)} mm")
        
    final_hhll_mm = final_hll_mm + user_hhll_margin
    st.success(f"📏 **Tank Bottom to HHLL** = {final_hll_mm} + {user_hhll_margin} = **{final_hhll_mm} mm**")

    st.write("---")
    st.markdown("### 🔹 Step 5: Total Tank Height (Tank Top)")
    overflow_req = st.radio("**5.1 Overflow Nozzle Required?**", ["No (Option A)", "Yes (Option B)"], key="t2_of_req")
    
    rule_95_margin, calc_overflow_noz_mm, selected_overflow_noz_mm, overflow_margin_calc = 0, 0, 150, 0
    
    if overflow_req == "No (Option A)":
        st.markdown("**Option A: No Overflow Nozzle**")
        st.write("📌 **Sizing Criteria:** Minimum 300 mm OR < 95% total tank height (includes thermal expansion).")
        rule_95_margin = final_hhll_mm * (0.05 / 0.95)
        suggested_top_margin = max(300.0, rule_95_margin)
        
        st.write(f"- Absolute Minimum = **300 mm**")
        st.write(f"- 95% Tank Height Rule Margin = HHLL ({final_hhll_mm}) × (0.05 / 0.95) = **{round(rule_95_margin, 2)} mm**")
        st.success(f"➔ **Calculated Top Margin** = Max(300, {round(rule_95_margin, 2)}) = **{round(suggested_top_margin)} mm**")
        
        t_col1, t_col2 = st.columns([1, 2])
        with t_col1:
            user_top_margin = st.number_input("Final Top Margin (mm) [User Input]", min_value=0, value=int(math.ceil(suggested_top_margin)), step=1, key="t2_top_m")
        with t_col2:
            st.info(f"💡 **Shell DEP Reference:** Minimum top margin for **{c['roof_type']}** is **{dep_top_margin} mm**.")
            
    else:
        st.markdown("**Option B: With Overflow Nozzle (Self-Venting)**")
        if c['q_fill_m3_s'] > 0:
            d_min_m = ((4 * c['q_fill_m3_s']) / (0.3 * math.pi * math.sqrt(9.81)))**(0.4)
            calc_overflow_noz_mm = d_min_m * 1000
            standard_sizes_overflow = [50, 75, 100, 150, 200, 250, 300, 350, 400, 500, 600, 750, 900, 1000, 1200]
            selected_overflow_noz_mm = next((size for size in standard_sizes_overflow if calc_overflow_noz_mm <= size), 1200)
        else:
            calc_overflow_noz_mm, selected_overflow_noz_mm = 0, 150
            
        st.write(f"- Calculated Overflow ID = **{round(calc_overflow_noz_mm, 2)} mm**")
        st.success(f"➔ **Selected Standard Overflow Nozzle (D) = {selected_overflow_noz_mm} mm**")
        st.latex(r"F_r = \frac{V}{\sqrt{g \cdot D}} < 0.3 \text{ (for self-venting)}")
        st.write("📌 **Sizing Criteria:** Minimum 300 mm OR Formula (1.5 × D + 150 mm).")
        
        overflow_margin_calc = (1.5 * selected_overflow_noz_mm) + 150
        suggested_top_margin = max(300.0, overflow_margin_calc)
        
        st.write(f"- Overflow Formula (1.5 × {selected_overflow_noz_mm} + 150) = **{overflow_margin_calc} mm**")
        st.write("- Absolute Minimum = **300 mm**")
        st.success(f"➔ **Calculated Top Margin** = Max(300, {overflow_margin_calc}) = **{round(suggested_top_margin)} mm**")
        
        t_col1, t_col2 = st.columns([1, 2])
        with t_col1:
            user_top_margin = st.number_input("Final Top Margin (mm) [User Input]", min_value=0, value=int(math.ceil(suggested_top_margin)), step=1, key="t2_top_m")
        with t_col2:
            st.info(f"💡 **Shell DEP Reference:** Minimum top margin for **{c['roof_type']}** is **{dep_top_margin} mm**.")
            
    # --- HEIGHT ROUNDING TO NEAREST 100mm FOR FABRICATION ---
    raw_top_mm = final_hhll_mm + user_top_margin
    final_top_mm = int(math.ceil(raw_top_mm / 100.0) * 100) # Rounds up to nearest 100 mm
    
    st.markdown("**5.3 Final Tank Height Calculation**")
    st.success(f"📏 **Raw Tank Height** = {final_hhll_mm} + {user_top_margin} = {int(raw_top_mm)} mm ➔ **Rounded Height for Fabrication = {final_top_mm} mm**")
    
    if overflow_req == "No (Option A)":
        actual_percentage = (final_hhll_mm / final_top_mm) * 100 if final_top_mm > 0 else 100
        if user_top_margin < 300: st.error("⚠️ Margin is less than absolute minimum 300 mm!")
        elif actual_percentage > 95: st.error(f"⚠️ HHLL exceeds 95% limit of total height!")
        else: st.success(f"✅ Safe! HHLL is {round(actual_percentage, 2)}% of total tank height.")
    else:
        if user_top_margin < overflow_margin_calc: st.warning(f"⚠️ Margin is less than Overflow calculation requirement!")
        elif user_top_margin < 300: st.warning("⚠️ Margin is less than absolute minimum 300 mm!")
        else: st.success("✅ Margin is safe and compliant with overflow logic.")

    # Returning ALL values to render the Dashboard in Tab 1 and Tab 3
    return {
        "sizing_basis": sizing_basis, "final_volume_m3": final_volume_m3, "calc_diameter_m": calc_diameter_m, "calc_area_m2": calc_area_m2,
        "calc_noz_mm": calc_noz_mm, "selected_noz_mm": selected_noz_mm, "nozzle_center_C": nozzle_center_C, "nozzle_radius_R": nozzle_radius_R,
        "vortex_margin_M": vortex_margin_M, "base_llll_mm": base_llll_mm, "dep_min_llll": dep_min_llll, "dep_top_margin": dep_top_margin,
        "final_llll_mm": final_llll_mm, "empty_time_min": empty_time_min, "empty_resp_mm_rise": empty_resp_mm_rise, 
        "suggested_lll_margin": suggested_lll_margin, "user_lll_margin": user_lll_margin, "final_lll_mm": final_lll_mm,
        "working_h_mm_suggested": working_h_mm_suggested, "user_working_height": user_working_height, "final_hll_mm": final_hll_mm,
        "fill_time_min": fill_time_min, "fill_resp_mm_rise": fill_resp_mm_rise, "suggested_hhll_margin": suggested_hhll_margin,
        "user_hhll_margin": user_hhll_margin, "final_hhll_mm": final_hhll_mm, "overflow_req": overflow_req, 
        "rule_95_margin": rule_95_margin, "calc_overflow_noz_mm": calc_overflow_noz_mm, "selected_overflow_noz_mm": selected_overflow_noz_mm,
        "overflow_margin_calc": overflow_margin_calc, "suggested_top_margin": suggested_top_margin, "user_top_margin": user_top_margin,
        "final_top_mm": final_top_mm
    }