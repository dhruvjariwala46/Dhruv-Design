# FILE NAME: app.py

import streamlit as st
import pandas as pd

# Yahan humne apni doosri files ko import kiya hai
import storage_tank as tank
import pressure_vessel as vessel

# ==========================================
# 1. PAGE SETUP
# ==========================================
st.set_page_config(page_title="Process Design Hub", page_icon="⚙️", layout="wide")

if 'equipment_db' not in st.session_state:
    st.session_state.equipment_db = {}

# ==========================================
# 2. LEFT SIDEBAR NAVIGATION
# ==========================================
st.sidebar.title("⚙️ Navigation Menu")
app_mode = st.sidebar.radio("Workspaces:", [
    "🛠️ 1. Equipment Sizing Desk", 
    "📋 2. Master Equipment List", 
    "📄 3. PDS Download Hub"
])
st.sidebar.divider()

# ==========================================
# 3. WORKSPACE 1: SIZING DESK
# ==========================================
if app_mode == "🛠️ 1. Equipment Sizing Desk":
    st.title("🛠️ Equipment Sizing Desk")
    
    col1, col2 = st.columns(2)
    with col1:
        eq_type = st.selectbox("1. Select Equipment Type:", ["Atmospheric Storage Tank", "Pressure Vessel"])
    with col2:
        standards = ["API 650", "API 620"] if eq_type == "Atmospheric Storage Tank" else ["ASME Section VIII"]
        eq_standard = st.selectbox("2. Select Design Standard:", standards)
        
    st.divider()
    
    # SYSTEM CALLING RESPECTIVE FILES DYNAMICALLY
    if eq_type == "Atmospheric Storage Tank":
        # Yeh line 'storage_tank.py' wale code ko chalu karti hai
        tank.run_storage_tank_sizing(eq_standard)
        
    elif eq_type == "Pressure Vessel":
        # Yeh line 'pressure_vessel.py' wale code ko chalu karti hai
        vessel.run_pressure_vessel_sizing(eq_standard)

# ==========================================
# WORKSPACE 2 & 3
# ==========================================
elif app_mode == "📋 2. Master Equipment List":
    st.title("📋 Master Equipment List")
    if st.session_state.equipment_db:
        st.dataframe(pd.DataFrame(list(st.session_state.equipment_db.values())), use_container_width=True)
    else:
        st.warning("Database is empty.")

elif app_mode == "📄 3. PDS Download Hub":
    st.title("📄 Process Data Sheet (PDS) Hub")
    if st.session_state.equipment_db:
        for tag, details in st.session_state.equipment_db.items():
            st.write(f"**{tag}** | Dia: {details['Dia (m)']}m, Height: {details['Total Height (m)']}m")