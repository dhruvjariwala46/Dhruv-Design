# FILE NAME: tab1_summary.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def _build_tank_schematic(roof_type, final_top_mm, final_hhll_mm, final_hll_mm, final_lll_mm, final_llll_mm, nozzle_center_C, calc_diameter_m):
    fig = go.Figure()
    TANK_X0, TANK_X1 = 0, 10
    TANK_MID = (TANK_X0 + TANK_X1) / 2
    roof_h = 0.06 * final_top_mm
    
    if "Fixed" in roof_type or "Dome" in roof_type:
        fig.add_shape(type="path", path=f"M {TANK_X0},{final_top_mm} L {TANK_MID},{final_top_mm + roof_h} L {TANK_X1},{final_top_mm} Z", line=dict(color="black", width=3), fillcolor="white")
    else:
        fig.add_shape(type="line", x0=TANK_X0 + 0.3, x1=TANK_X1 - 0.3, y0=final_hll_mm, y1=final_hll_mm, line=dict(color="#555555", width=3))
        fig.add_annotation(x=TANK_X1 - 0.3, y=final_hll_mm, text="Floating Roof", showarrow=False, xshift=55, font=dict(size=9, color="#555555"))
        
    fig.add_shape(type="rect", x0=TANK_X0, x1=TANK_X1, y0=0, y1=final_top_mm, line=dict(color="black", width=3))
    fig.add_shape(type="rect", x0=TANK_X0, x1=TANK_X1, y0=final_lll_mm, y1=final_hll_mm, fillcolor="rgba(173, 216, 230, 0.4)", line_width=0)
    
    levels_list = [
        ("Tank Top", final_top_mm, "black"), ("HHLL", final_hhll_mm, "red"),
        ("HLL", final_hll_mm, "blue"), ("LLL", final_lll_mm, "orange"),
        ("LLLL", final_llll_mm, "red"), ("Tank Bottom", 0, "black")
    ]
    for name, h, col in levels_list:
        fig.add_shape(type="line", x0=TANK_X0, x1=TANK_X1, y0=h, y1=h, line=dict(color=col, width=1.5, dash="dash"))
        fig.add_annotation(x=TANK_MID, y=h, text=f"<b>{name} ({int(round(h))} mm)</b>", showarrow=False, yshift=10, font=dict(color=col, size=11))
        
    fig.add_shape(type="rect", x0=TANK_X1, x1=TANK_X1 + 0.5, y0=nozzle_center_C - 30, y1=nozzle_center_C + 30, line=dict(color="black", width=2), fillcolor="white")
    fig.add_shape(type="line", x0=TANK_X1 + 0.5, x1=TANK_X1 + 0.5, y0=nozzle_center_C - 45, y1=nozzle_center_C + 45, line=dict(color="black", width=3))
    
    def witness(x_from, x_to, y, color="#aaaaaa"):
        fig.add_shape(type="line", x0=x_from, x1=x_to, y0=y, y1=y, line=dict(color=color, width=1, dash="dot"))
    def v_dim(x, y0, y1, text, color="#222222", dx=8, size=10):
        fig.add_annotation(x=x, y=y1, ax=x, ay=y0, xref="x", yref="y", axref="x", ayref="y", showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.3, arrowcolor=color, text="")
        fig.add_annotation(x=x, y=y0, ax=x, ay=y1, xref="x", yref="y", axref="x", ayref="y", showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.3, arrowcolor=color, text="")
        fig.add_annotation(x=x, y=(y0 + y1) / 2, text=text, showarrow=False, xshift=dx, xanchor="left", font=dict(size=size, color=color))
        
    dim_x1 = TANK_X1 + 1.3
    for y in [0, final_llll_mm, final_lll_mm, final_hll_mm, final_hhll_mm, final_top_mm]: witness(TANK_X1, dim_x1, y)
    v_dim(dim_x1, 0, final_llll_mm, f"<b>H1</b> = {int(final_llll_mm)} mm")
    v_dim(dim_x1, final_llll_mm, final_lll_mm, f"<b>Hb</b> = {int(final_lll_mm - final_llll_mm)} mm")
    v_dim(dim_x1, final_lll_mm, final_hll_mm, f"<b>Hw</b> = {int(final_hll_mm - final_lll_mm)} mm")
    v_dim(dim_x1, final_hll_mm, final_hhll_mm, f"<b>Ht</b> = {int(final_hhll_mm - final_hll_mm)} mm")
    v_dim(dim_x1, final_hhll_mm, final_top_mm, f"<b>H2</b> = {int(final_top_mm - final_hhll_mm)} mm")
    
    witness(TANK_X0 - 1.5, TANK_X0, 0)
    witness(TANK_X0 - 1.5, TANK_X0, final_top_mm)
    v_dim(TANK_X0 - 1.5, 0, final_top_mm, f"<b>H</b> = {round(final_top_mm / 1000, 2)} m", dx=-72)
    
    d_y = -0.08 * final_top_mm
    fig.add_shape(type="line", x0=TANK_X0, x1=TANK_X0, y0=0, y1=d_y, line=dict(color="#aaaaaa", width=1, dash="dot"))
    fig.add_shape(type="line", x0=TANK_X1, x1=TANK_X1, y0=0, y1=d_y, line=dict(color="#aaaaaa", width=1, dash="dot"))
    fig.add_annotation(x=TANK_X0, y=d_y, ax=TANK_X1, ay=d_y, xref="x", yref="y", axref="x", ayref="y", showarrow=True, arrowhead=2, arrowwidth=1.3, arrowcolor="#222222", text="")
    fig.add_annotation(x=TANK_X1, y=d_y, ax=TANK_X0, ay=d_y, xref="x", yref="y", axref="x", ayref="y", showarrow=True, arrowhead=2, arrowwidth=1.3, arrowcolor="#222222", text="")
    
    # Correct variable name for diameter
    fig.add_annotation(x=TANK_MID, y=d_y, text=f"<b>D</b> = {calc_diameter_m} m", showarrow=False, yshift=-14, font=dict(size=11, color="#222222"))
    
    fig.update_layout(
        title=dict(text="Tank Elevation Schematic", font=dict(size=16)),
        xaxis=dict(visible=False, range=[TANK_X0 - 4, dim_x1 + 7]),
        yaxis=dict(title="Height (mm)", showgrid=False, range=[d_y * 1.6, final_top_mm * 1.15 + roof_h], autorange=False),
        height=700, margin=dict(l=10, r=10, t=40, b=10), plot_bgcolor="white",
        uirevision=str(round(final_top_mm, 1)) + roof_type, showlegend=False
    )
    return fig

def _build_summary_table(calc_area_m2, final_top_mm, final_hhll_mm, final_hll_mm, final_lll_mm, final_llll_mm, vol_empty_m3_hr):
    v_total = calc_area_m2 * (final_top_mm / 1000)
    v_net_dead = calc_area_m2 * (final_hhll_mm / 1000)
    v_net = calc_area_m2 * ((final_hhll_mm - final_llll_mm) / 1000)
    v_working = calc_area_m2 * ((final_hll_mm - final_lll_mm) / 1000)
    v_dead = calc_area_m2 * (final_llll_mm / 1000)
    v_free = calc_area_m2 * ((final_top_mm - final_hhll_mm) / 1000)
    holdup_hr_final = v_working / vol_empty_m3_hr if vol_empty_m3_hr > 0 else 0
    
    summary_data = {
        "Description": ["Total capacity", "Net Capacity + Dead Volume", "Net Capacity", "Working volume/ capacity", "Dead Volume", "Free Volume", "Hold-up time"],
        "Remarks": [
            f"Total tank volume upto tank top i.e. {final_top_mm} mm", f"Tank bottom upto HHLL i.e. {final_hhll_mm} mm",
            f"Between trips i.e. HHLL ({final_hhll_mm}mm) & LLLL ({final_llll_mm}mm)", f"Between i.e. HLL ({final_hll_mm}mm) & LLL ({final_lll_mm}mm)",
            f"Below pump trip level LLLL ({final_llll_mm}mm) upto tank bottom", f"Volume above HHLL ({final_hhll_mm} mm) upto tank height",
            "(based on Working capacity & outflow rate)"
        ],
        "Value": [round(v_total, 1), round(v_net_dead, 1), round(v_net, 1), round(v_working, 1), round(v_dead, 1), round(v_free, 1), round(holdup_hr_final, 2)],
        "Unit": ["m³", "m³", "m³", "m³", "m³", "m³", "hr"]
    }
    return pd.DataFrame(summary_data)

def render(c, t2):
    st.markdown("### 📊 Sizing Dashboard & Final Sketch")
    st.info("💡 Note: To modify these final dimensions, please adjust the inputs inside **Tab 2: Inputs & Detailed Calc**.")
    
    fig = _build_tank_schematic(
        c['roof_type'], 
        t2['final_top_mm'], 
        t2['final_hhll_mm'], 
        t2['final_hll_mm'], 
        t2['final_lll_mm'], 
        t2['final_llll_mm'], 
        t2['nozzle_center_C'], 
        t2['calc_diameter_m']
    )
    st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': False})
    
    st.markdown("""
    **📐 Nomenclature (Dimension Key for Sketch):**
    * **H1 (Base Level):** Distance from Tank Bottom to LLLL.
    * **Hb (Emptying Margin):** Buffer height for Operator Response (LLLL to LLL).
    * **Hw (Working Height):** Net Working Capacity height (LLL to HLL).
    * **Ht (Filling Margin):** Buffer height for Operator Response (HLL to HHLL).
    * **H2 (Top Freeboard):** Safe vapor space / overflow margin (HHLL to Tank Top).
    * **H (Total Shell Height):** Overall cylindrical shell height.
    * **D (Tank Diameter):** Calculated inner diameter of the tank.
    """)

    st.write("---")
    st.markdown("#### 📊 Volume Summary Table")
    summary_df = _build_summary_table(
        t2['calc_area_m2'], 
        t2['final_top_mm'], 
        t2['final_hhll_mm'], 
        t2['final_hll_mm'], 
        t2['final_lll_mm'], 
        t2['final_llll_mm'], 
        c['vol_empty_m3_hr']
    )
    st.dataframe(summary_df, hide_index=True, use_container_width=True)
    
    if st.button("Save Verified Design to Master List 💾", type="primary"):
        if c['tag_no'] == "": 
            st.error("Error: Tag Number is mandatory!")
        else:
            st.session_state.equipment_db[c['tag_no']] = {
                "Tag": c['tag_no'], "Equipment": "Tank", "Standard": c['eq_standard'], "Roof": c['roof_type'],
                "Working Vol (m³)": round(t2['final_volume_m3'], 2), "Dia (m)": t2['calc_diameter_m'], "Total Height (m)": round(t2['final_top_mm'] / 1000, 2),
                "LLLL (mm)": t2['final_llll_mm'], "LLL (mm)": t2['final_lll_mm'], "HLL (mm)": t2['final_hll_mm'], "HHLL (mm)": t2['final_hhll_mm']
            }
            st.success(f"Success! {c['tag_no']} has been sized securely and added to the Master List.")