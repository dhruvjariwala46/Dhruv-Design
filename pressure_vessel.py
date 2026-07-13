# FILE NAME: pressure_vessel.py

import streamlit as st

def run_pressure_vessel_sizing(eq_standard):
    st.subheader(f"Input Parameters ({eq_standard})")
    pv_tag = st.text_input("Tag Number", placeholder="e.g., V-1001").strip().upper()
    tvp_pv = st.number_input("TVP (kPaa)", min_value=0.0, value=150.0, help="True Vapor Pressure at operating temp")
    
    st.write("---")
    st.markdown("### 🔹 Design Validation")
    if tvp_pv <= 75:
        st.warning("⚠️ **Optimization Tip:** TVP is ≤ 75 kPaa. Designing a Pressure Vessel (ASME Sec VIII) might be overly expensive. Consider using an **API 650** or **API 620** tank.")
    else:
        st.success("✅ TVP > 75 kPaa. ASME Section VIII is the correct design standard!")
        
    st.info("🔒 Sizing module for Pressure Vessels is under development. Coming soon!")