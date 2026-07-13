# FILE NAME: tab3_nozzles.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import math

# --- SMART SIZE PARSER ---
def _parse_size(val):
    try:
        return float(str(val).upper().split('X')[0].strip())
    except:
        return 150.0

# --- HELPER FUNCTION: PROFESSIONAL GA DRAWING (SIDE VIEW) ---
def _build_ga_drawing(c, t2, nozzles_df):
    fig = go.Figure()
    
    # Dimensions in mm
    D = t2['calc_diameter_m'] * 1000  
    H = t2['final_top_mm']
    
    # Roof Height Calculation (Approx 6% of Top Height for Dome/Cone)
    if "Fixed" in c['roof_type'] or "Dome" in c['roof_type']:
        roof_H = H + (0.06 * H)
    else:
        roof_H = H
        
    # 1. TANK SHELL & BOTTOM
    fig.add_shape(type="rect", x0=0, x1=D, y0=0, y1=H, line=dict(color="black", width=3), fillcolor="white")
    
    # 2. ROOF
    if roof_H > H:
        fig.add_shape(type="path", path=f"M 0,{H} L {D/2},{roof_H} L {D},{H} Z", line=dict(color="black", width=3), fillcolor="white")
    else:
        # Floating roof representation
        fig.add_shape(type="line", x0=0, x1=D, y0=t2['final_hll_mm'], y1=t2['final_hll_mm'], line=dict(color="grey", width=3, dash="dash"))
        
    # 3. CENTER TEXT (TAG & LEVELS)
    levels_list = [
        ("HHLL", t2['final_hhll_mm']), ("HLL", t2['final_hll_mm']),
        ("LLL", t2['final_lll_mm']), ("LLLL", t2['final_llll_mm'])
    ]
    text_levels = f"<b>{c['tag_no']}</b>"
    for name, h in levels_list:
        fig.add_shape(type="line", x0=0, x1=D, y0=h, y1=h, line=dict(color="rgba(0,0,0,0.15)", width=1, dash="dash"))
        text_levels += f"<br>{name}: {int(h)} mm"
        
    fig.add_annotation(x=D/2, y=H*0.75, text=text_levels, showarrow=False, font=dict(size=12, color="black"))

    # 4. BOTTOM SLOPE SYMBOL
    fig.add_shape(type="path", path=f"M {D/2 - D*0.1}, {H*0.03} L {D/2 + D*0.1}, {H*0.03} L {D/2 + D*0.1}, {H*0.07} Z", line=dict(color="black", width=2))
    fig.add_annotation(x=D/2, y=H*0.09, text="1% SLOPE", showarrow=False, font=dict(size=10, color="black"))

    # 5. ID (DIAMETER) DIMENSION LINE
    fig.add_annotation(x=D/2, y=H*0.35, text=f"ID = {int(D)} mm", showarrow=False, yshift=10, font=dict(size=11, color="black"))
    fig.add_annotation(x=0, y=H*0.35, ax=D, ay=H*0.35, xref="x", yref="y", axref="x", ayref="y", showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.5, arrowcolor="black")
    fig.add_annotation(x=D, y=H*0.35, ax=0, ay=H*0.35, xref="x", yref="y", axref="x", ayref="y", showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.5, arrowcolor="black")

    # 6. TOTAL HEIGHT DIMENSION LINE
    offset = max(D * 0.30, 2000) 
    dim_x = D + offset * 0.85
    
    fig.add_shape(type="line", x0=D, x1=D+offset, y0=0, y1=0, line=dict(color="black", width=1.5))
    fig.add_shape(type="line", x0=D, x1=D+offset, y0=roof_H, y1=roof_H, line=dict(color="black", width=1.5))
    
    fig.add_annotation(x=dim_x + (D*0.05), y=roof_H/2, text=f"H = {int(roof_H)} mm", textangle=90, showarrow=False, font=dict(size=12, color="black"))
    fig.add_annotation(x=dim_x, y=0, ax=dim_x, ay=roof_H, xref="x", yref="y", axref="x", ayref="y", showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.5, arrowcolor="black")
    fig.add_annotation(x=dim_x, y=roof_H, ax=dim_x, ay=0, xref="x", yref="y", axref="x", ayref="y", showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.5, arrowcolor="black")

    # ==========================================
    # 7. DRAWING NOZZLES ON THE ELEVATION
    # ==========================================
    roof_n, left_n, right_n = [], [], []
    
    for idx, row in nozzles_df.iterrows():
        pos = str(row.get('Position', 'Shell')).upper()
        s = str(row['Service']).upper()
        
        if "ROOF" in pos:
            roof_n.append(row)
        else: # SHELL
            if "OVERFLOW" in s or "DRAIN" in s or "INSTRUMENT" in s:
                left_n.append(row)
            elif "PUMP" in s or "OUTLET" in s or "MANWAY" in s:
                right_n.append(row)
            else:
                if len(left_n) <= len(right_n): left_n.append(row)
                else: right_n.append(row)

    # 7A. Draw Roof Nozzles
    for i, row in enumerate(roof_n):
        x = (i + 1) * (D / (len(roof_n) + 1))
        if x <= D/2: y_base = H + (x/(D/2))*(roof_H - H)
        else: y_base = H + ((D-x)/(D/2))*(roof_H - H)

        n_len = H * 0.05
        flange_w = _parse_size(row['Size (mm)']) * 1.5 + 50
        
        if "MANWAY" in str(row['Service']).upper() or row['Mark'].upper() == "M1": 
            flange_w, n_len = 600, H * 0.08
            
        fig.add_shape(type="line", x0=x, x1=x, y0=y_base, y1=y_base+n_len, line=dict(color="black", width=2))
        fig.add_shape(type="line", x0=x-flange_w/2, x1=x+flange_w/2, y0=y_base+n_len, y1=y_base+n_len, line=dict(color="black", width=3))
        fig.add_annotation(x=x, y=y_base+n_len, text=row['Mark'], showarrow=False, yshift=15, font=dict(size=10, color="black"))
        
        internals = str(row['Internals']).upper()
        if "DIP" in internals:
            fig.add_shape(type="line", x0=x, x1=x, y0=y_base, y1=H*0.2, line=dict(color="blue", dash="dot", width=2))
        elif "J-PIPE" in internals or "DEFLECT" in internals:
            fig.add_shape(type="path", path=f"M {x},{y_base} L {x},{y_base - H*0.1} Q {x},{y_base - H*0.15} {x+D*0.05},{y_base - H*0.15}", line=dict(color="green", width=2))

    # 7B. Draw Left Shell Nozzles
    for i, row in enumerate(left_n):
        y = (i + 1) * (H / (len(left_n) + 1))
        
        if "OVERFLOW" in str(row['Service']).upper(): y = t2['final_hhll_mm']
        elif "DRAIN" in str(row['Service']).upper(): y = H * 0.08 
        
        n_len = D * 0.05
        flange_w = _parse_size(row['Size (mm)']) * 1.5 + 50
        
        if "MANWAY" in str(row['Service']).upper(): flange_w = 600
        
        fig.add_shape(type="line", x0=0, x1=-n_len, y0=y, y1=y, line=dict(color="black", width=2))
        fig.add_shape(type="line", x0=-n_len, x1=-n_len, y0=y-flange_w/2, y1=y+flange_w/2, line=dict(color="black", width=3))
        fig.add_annotation(x=-n_len, y=y, text=row['Mark'], showarrow=False, xshift=-20, font=dict(size=10, color="black"))
        
        internals = str(row['Internals']).upper()
        if "DIP" in internals:
            fig.add_shape(type="line", x0=0, x1=D*0.15, y0=y, y1=y - H*0.1, line=dict(color="blue", dash="dot", width=2))
        elif "J-PIPE" in internals or "DEFLECT" in internals:
            fig.add_shape(type="path", path=f"M 0,{y} L {D*0.05},{y} Q {D*0.08},{y} {D*0.08},{y-H*0.05}", line=dict(color="green", width=2))

    # 7C. Draw Right Shell Nozzles
    for i, row in enumerate(right_n):
        y = (i + 1) * (H / (len(right_n) + 1))
        
        if "PUMP" in str(row['Service']).upper() or "OUTLET" in str(row['Service']).upper(): y = t2['final_llll_mm']
        
        flange_w = _parse_size(row['Size (mm)']) * 1.5 + 50
        
        if "MANWAY" in str(row['Service']).upper(): 
            y, flange_w = H * 0.2, 600
            
        n_len = D * 0.05
        fig.add_shape(type="line", x0=D, x1=D+n_len, y0=y, y1=y, line=dict(color="black", width=2))
        fig.add_shape(type="line", x0=D+n_len, x1=D+n_len, y0=y-flange_w/2, y1=y+flange_w/2, line=dict(color="black", width=3))
        fig.add_annotation(x=D+n_len, y=y, text=row['Mark'], showarrow=False, xshift=20, font=dict(size=10, color="black"))

        internals = str(row['Internals']).upper()
        if "DIP" in internals:
            fig.add_shape(type="line", x0=D, x1=D-D*0.15, y0=y, y1=y - H*0.1, line=dict(color="blue", dash="dot", width=2))
        elif "J-PIPE" in internals or "DEFLECT" in internals:
            fig.add_shape(type="path", path=f"M {D},{y} L {D-D*0.05},{y} Q {D-D*0.08},{y} {D-D*0.08},{y-H*0.05}", line=dict(color="green", width=2))

    # Cleanup layout
    max_x = D + offset * 1.2
    min_x = -max(D * 0.2, 1000)
    fig.update_layout(
        title=dict(text="Side View (GA Elevation)", font=dict(size=16)),
        xaxis=dict(visible=False, range=[min_x, max_x]),
        yaxis=dict(visible=False, range=[-H*0.1, roof_H*1.2], scaleanchor="x", scaleratio=1),
        height=750, margin=dict(l=20, r=20, t=60, b=20), plot_bgcolor="white",
        showlegend=False
    )
    return fig


# --- MAIN RENDER LOGIC ---
def render(c, t2):
    st.markdown("### 🚰 Dynamic Nozzle Schedule & GA Drawings")
    # ERROR YAHAN THA: c['calc_diameter_m'] ko t2['calc_diameter_m'] kar diya gaya hai 👇
    st.write(f"Tank circumference and physical space is strictly verified against a diameter of **{t2['calc_diameter_m']} m**.")
    st.info("🗑️ **To Delete a Nozzle:** Table ke left me bani choti Checkbox ko tick karein aur keyboard par 'Delete' dabayein.")
    
    mark_opts = [f"N{i}" for i in range(1, 21)] + [f"M{i}" for i in range(1, 6)] + \
                [f"LG{i}" for i in range(1, 5)] + [f"SG{i}" for i in range(1, 5)] + [f"I{i}" for i in range(1, 10)] + [f"OF{i}" for i in range(1, 4)]
    
    size_options = ["25", "50", "80x50", "75", "100", "100x50", "100x80", "150", "150x100", "200", "250", "300", "350", "400", "500", "600", "750", "900", "1000", "1200"]
    
    default_nozzles = [
        {"Mark": "N1", "Position": "Shell", "Service": "Pump-out / Outlet", "Size (mm)": str(int(t2['selected_noz_mm'])), "Flange Rating": "150# RF", "Internals": "Vortex Breaker", "Remarks": ""}
    ]
    if t2['overflow_req'] == "Yes (Option B)":
        default_nozzles.append({"Mark": "OF1", "Position": "Shell", "Service": "Overflow", "Size (mm)": str(int(t2['selected_overflow_noz_mm'])), "Flange Rating": "150# RF", "Internals": "None", "Remarks": ""})
        
    default_nozzles.extend([
        {"Mark": "N2", "Position": "Roof", "Service": "Inlet", "Size (mm)": "150", "Flange Rating": "150# RF", "Internals": "J-Pipe / Deflector", "Remarks": ""},
        {"Mark": "N3", "Position": "Shell", "Service": "Drain", "Size (mm)": "50", "Flange Rating": "150# RF", "Internals": "None", "Remarks": ""},
        {"Mark": "N4", "Position": "Roof", "Service": "Vent", "Size (mm)": "200", "Flange Rating": "Atmospheric / Open", "Internals": "None", "Remarks": ""},
        {"Mark": "N7", "Position": "Shell", "Service": "Instrument", "Size (mm)": "80x50", "Flange Rating": "150# RF", "Internals": "Dip Pipe", "Remarks": "80mm Flange with 50mm Int. Pipe"},
        {"Mark": "M1", "Position": "Roof", "Service": "Manway (Roof)", "Size (mm)": "600", "Flange Rating": "150# RF", "Internals": "None", "Remarks": ""},
        {"Mark": "M2", "Position": "Shell", "Service": "Manway (Shell)", "Size (mm)": "600", "Flange Rating": "150# RF", "Internals": "None", "Remarks": ""}
    ])
    
    df_nozzles = pd.DataFrame(default_nozzles)
    
    st.caption("👇 Add new nozzles below. Use **Remarks** to add detailed notes. Select **Roof** or **Shell** to determine position.")
    edited_nozzles = st.data_editor(
        df_nozzles,
        num_rows="dynamic",
        column_config={
            "Mark": st.column_config.SelectboxColumn("Nozzle Mark", options=mark_opts, required=True),
            "Position": st.column_config.SelectboxColumn("Position", options=["Roof", "Shell"], required=True),
            "Service": st.column_config.SelectboxColumn("Service / Type", options=["Inlet", "Pump-out / Outlet", "Overflow", "Vent", "Drain", "Manway (Roof)", "Manway (Shell)", "Instrument", "Level Instrument", "Sight Glass", "Light Glass", "Nitrogen Inlet", "Spare"], required=True),
            "Size (mm)": st.column_config.SelectboxColumn("Size (mm)", options=size_options, required=True),
            "Flange Rating": st.column_config.SelectboxColumn("Flange Rating", options=["150# RF", "150# FF", "300# RF", "Atmospheric / Open"], required=True),
            "Internals": st.column_config.SelectboxColumn("Internals", options=["None", "Vortex Breaker", "Dip Pipe", "J-Pipe / Deflector", "Stilling Well"]),
            "Remarks": st.column_config.TextColumn("Remarks", default="")
        },
        use_container_width=True,
        key="t3_nozzle_table"
    )
    
    duplicates = edited_nozzles[edited_nozzles.duplicated('Mark', keep=False)]['Mark'].unique()
    if len(duplicates) > 0:
        st.error(f"🚨 **Validation Error:** Nozzle Marks must be unique! Duplicate found: **{', '.join(duplicates)}**")
        st.stop()
    
    tank_dia_mm = t2['calc_diameter_m'] * 1000
    assigned_nozzles = []
    angles = []
    clash_warnings = []
    
    for idx, row in edited_nozzles.iterrows():
        mark = str(row.get('Mark', '')).strip().upper()
        service = str(row.get('Service', '')).strip().upper()
        size = _parse_size(row.get('Size (mm)', '150'))
            
        if "VENT" in service: pref = 180
        elif "NITROGEN" in service or "INLET" in service: pref = 90
        elif "OVERFLOW" in service: pref = 0
        elif mark.startswith("SG") or "SIGHT" in service: pref = 315
        elif mark.startswith("LG") or "LIGHT" in service or "LEVEL" in service: pref = 135
        elif "OUTLET" in service or "PUMP" in service: pref = 270
        elif mark.startswith("M") or "MANWAY" in service: pref = 45
        elif "DRAIN" in service: pref = 180
        else: pref = 0
            
        placed = False
        for offset in [0, 15, -15, 30, -30, 45, -45, 60, -60, 75, -75, 90, -90, 105, -105, 120, -120]:
            test_angle = (pref + offset) % 360
            clash = False
            for an in assigned_nozzles:
                req_clearance = ((size * 1.5 + 75) / 2) + ((an['Size'] * 1.5 + 75) / 2) + 100
                diff = abs(test_angle - an['Angle'])
                diff = min(diff, 360 - diff)
                arc_length = (diff / 360.0) * (math.pi * tank_dia_mm)
                if arc_length < req_clearance:
                    clash = True
                    break
            if not clash:
                assigned_nozzles.append({'Mark': row['Mark'], 'Angle': test_angle, 'Size': size})
                angles.append(test_angle)
                placed = True
                if offset != 0: clash_warnings.append(f"🔄 Shifted **{row['Mark']}** by {offset}° to avoid physical clash with an adjacent nozzle.")
                break
                
        if not placed:
            angles.append(pref)
            clash_warnings.append(f"🚨 **CRITICAL OVERLAP:** Tank diameter ({t2['calc_diameter_m']}m) is too small to fit **{row['Mark']}** without clashing!")
            
    edited_nozzles['Angle'] = angles
    if clash_warnings:
        for w in clash_warnings:
            if "CRITICAL" in w: st.error(w)
            else: st.warning(w)

    st.write("---")
    st.markdown("#### 🧭 General Arrangement (GA) - Elevation View")
    fig_side = _build_ga_drawing(c, t2, edited_nozzles)
    st.plotly_chart(fig_side, use_container_width=True, config={'scrollZoom': False})
    
    st.write("---")
    st.markdown("#### 🧭 General Arrangement (GA) - Top Orientation View")
    
    fig_polar = go.Figure()
    fig_polar.add_trace(go.Scatterpolar(
        r=[1]*360, theta=list(range(360)), mode='lines', line=dict(color='black', width=4), name='Tank Shell', hoverinfo='skip'
    ))
        
    if not edited_nozzles.empty:
        fig_polar.add_trace(go.Scatterpolar(
            r=[1.15]*len(edited_nozzles), theta=edited_nozzles['Angle'], mode='markers+text',
            marker=dict(size=12, symbol="square", color='red', line=dict(width=1, color="black")),
            text=edited_nozzles['Mark'], textposition="top center",
            textfont=dict(size=13, color="blue", family="Arial Black"), name='Nozzles'
        ))
        
    fig_polar.update_layout(
        polar=dict(angularaxis=dict(direction="clockwise", rotation=90, showticklabels=True), radialaxis=dict(visible=False, range=[0, 1.45])),
        showlegend=False, height=650, margin=dict(t=60, b=40, l=40, r=40)
    )
    st.plotly_chart(fig_polar, use_container_width=True, config={'displayModeBar': False})
    
    # Return statement zaroori hai Tab 5 (PDS Export) ke liye
    return {
        "nozzles_df": edited_nozzles,
        "fig_side": fig_side,
        "fig_polar": fig_polar
    }