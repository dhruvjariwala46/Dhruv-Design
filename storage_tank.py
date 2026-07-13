# FILE NAME: storage_tank.py

import streamlit as st
import tab1_summary
import tab2_calc
import tab3_nozzles
import tab4_guide
import tab5_pds  # Naya module for PDS Export

def run_storage_tank_sizing(eq_standard):
    
    # --- ROW 1: General Info ---
    c1, c2, c3 = st.columns(3)
    with c1: tag_no = st.text_input("Tag Number", placeholder="e.g., TK-1001", key="main_tag").strip().upper()
    with c2: fluid = st.text_input("Fluid Handled", value="Raw Water", key="main_fluid")
    with c3:
        if eq_standard == "API 650": 
            roof_type = st.selectbox("Roof Type", ["Fixed Roof", "External Floating Roof", "Internal Floating Roof (D<15m)", "Internal Floating Roof (D>15m)"], key="main_roof")
        else:
            roof_type = "Fixed Dome Roof (API 620)"
            st.info("ℹ️ API 620 uses a gas-tight Fixed Dome Roof.")
            
    # --- ROW 2: Process Flow & Properties ---
    c4, c5, c6, c7, c8 = st.columns(5)
    with c4: max_fill_rate = st.number_input("Max Fill (kg/hr)", min_value=0.0, value=50000.0, step=1000.0, key="main_fill_rt")
    with c5: max_empty_rate = st.number_input("Max Empty (kg/hr)", min_value=0.0, value=50000.0, step=1000.0, key="main_empty_rt")
    with c6: density = st.number_input("Density (kg/m³)", min_value=1.0, value=1000.0, key="main_dens")
    with c7: empty_velocity = st.number_input("Emptying Velocity (m/s)", min_value=0.1, value=0.5, step=0.1, key="main_vel")
    with c8: tvp = st.number_input("TVP (kPaa)", min_value=0.0, value=5.0, key="main_tvp")
    
    if empty_velocity != 0.5:
        st.error("⚠️ Mandatory Rule: Emptying velocity must be 0.5 m/s.")
        forced_velocity = 0.5
    else: forced_velocity = 0.5
        
    is_tvp_valid = True
    if eq_standard == "API 650":
        if tvp > 75: st.error("🛑 TVP is > 75 kPaa! API 650 limit exceeded."); is_tvp_valid = False
        elif tvp > 10 and "Fixed" in roof_type: st.error("🛑 For TVP > 10 kPaa, a Fixed Roof is NOT allowed."); is_tvp_valid = False
    elif eq_standard == "API 620":
        if tvp > 75: st.error("🛑 TVP is > 75 kPaa! Select Pressure Vessel."); is_tvp_valid = False
            
    if is_tvp_valid:
        vol_fill_m3_hr = max_fill_rate / density if density > 0 else 0
        vol_empty_m3_hr = max_empty_rate / density if density > 0 else 0
        q_fill_m3_s = vol_fill_m3_hr / 3600
        q_empty_m3_s = vol_empty_m3_hr / 3600
        max_vol_flow_hr = max(vol_fill_m3_hr, vol_empty_m3_hr)
        
        main_data = {
            "eq_standard": eq_standard, "roof_type": roof_type, "tag_no": tag_no, "fluid": fluid,
            "max_vol_flow_hr": max_vol_flow_hr, "vol_empty_m3_hr": vol_empty_m3_hr, 
            "vol_fill_m3_hr": vol_fill_m3_hr, "q_empty_m3_s": q_empty_m3_s, "q_fill_m3_s": q_fill_m3_s,
            "forced_velocity": forced_velocity
        }

        # TAB 5 ADD KIYA HAI YAHAN PE
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Tab 1: Dashboard", "📐 Tab 2: Detailed Calc", "🚰 Tab 3: Nozzles", "📘 Tab 4: Guide", "📄 Tab 5: PDS Export"])
        
        with tab2:
            t2_results = tab2_calc.render(main_data)
            
        with tab1:
            if t2_results:
                tab1_summary.render(main_data, t2_results)
            
        with tab3:
            if t2_results:
                t3_results = tab3_nozzles.render(main_data, t2_results)
            
        with tab4:
            tab4_guide.render()
            
        # NAYA TAB 5 CALL HO RAHA HAI YAHAN
        with tab5:
            if t2_results and 't3_results' in locals() and t3_results:
                tab5_pds.render(main_data, t2_results, t3_results)
            else:
                 st.info("⚠️ Please complete the calculation and nozzle schedule first.")