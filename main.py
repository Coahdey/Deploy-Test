# -*- coding: utf-8 -*-
"""
Created on Tue Oct 28 23:49:48 2025

@author: yangshin.liu
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io


st.set_page_config(layout="wide")

st.title("CMP Zone Pressure & Polish Rate Input Tables")

# ---------- Table 1: Zone Pressures (wafer × zones) ----------
zone_names = [f"A{i}" for i in range(1, 9)]
wafer_names = [f"W{i}" for i in range(1, 13)]
zone_pressure_df = pd.DataFrame('', index=wafer_names, columns=zone_names)

# ---------- Table 2: Polish Profile (wafer × positions) ----------
positions = [
    -149, -147.979, -146.958, -145.938, -144.917, -143.896, -142.875, -141.854, -140.833, -139.813,
    -138.792, -137.771, -136.75, -135.729, -134.708, -133.688, -132.667, -131.646, -130.625, -129.604,
    -128.583, -127.563, -126.542, -125.521, -124.5, -123.479, -122.458, -121.438, -120.417, -119.396,
    -118.375, -117.354, -116.333, -115.313, -114.292, -113.271, -112.25, -111.229, -110.208, -109.188,
    -108.167, -107.146, -106.125, -105.104, -104.083, -103.063, -102.042, -101.021, -100, -99,
    -94.875, -90.75, -86.625, -82.5, -78.375, -74.25, -70.125, -66, -61.875, -57.75, -53.625, -49.5,
    -45.375, -41.25, -37.125, -33, -28.875, -24.75, -20.625, -16.5, -12.375, -8.25, -4.125, 0, 4.125,
    8.25, 12.375, 16.5, 20.625, 24.75, 28.875, 33, 37.125, 41.25, 45.375, 49.5, 53.625, 57.75, 61.875,
    66, 70.125, 74.25, 78.375, 82.5, 86.625, 90.75, 94.875, 99, 100, 101.021, 102.042, 103.063, 104.083,
    105.104, 106.125, 107.146, 108.167, 109.188, 110.208, 111.229, 112.25, 113.271, 114.292, 115.313,
    116.333, 117.354, 118.375, 119.396, 120.417, 121.438, 122.458, 123.479, 124.5, 125.521, 126.542,
    127.563, 128.583, 129.604, 130.625, 131.646, 132.667, 133.688, 134.708, 135.729, 136.75, 137.771,
    138.792, 139.813, 140.833, 141.854, 142.875, 143.896, 144.917, 145.938, 146.958, 147.979, 149
]
polish_profile_df = pd.DataFrame('', index=wafer_names, columns=positions)

col1, col2 = st.columns(2)

# --------- Editable Table for Pressures ---------
with col1:
    st.subheader("Zone Pressure Table")
    st.write("Paste your zone pressure data (Wafers × Zones):")
    zone_pressure_data = st.data_editor(zone_pressure_df, use_container_width=True, key="zone_pressure")

# --------- Editable Table for Polish Profile ---------
with col2:
    st.subheader("Polish Profile Table")
    st.write("Paste your polish profile data (Wafers × Positions):")
    polish_profile_data = st.data_editor(polish_profile_df, use_container_width=True, key="polish_profile")



st.info("Fill in the tables above (supports copy-paste from Excel). These data will be used for subsequent optimization and analysis.")

if st.button("Submit"):
    st.success("Calculating results...")

    ### --- Uniformity metrics per wafer ---
    results = []
    for wafer in wafer_names:
        row = polish_profile_data.loc[wafer]
        data = pd.to_numeric(row, errors='coerce').dropna().values
        if len(data) > 0:
            mean = np.mean(data)
            std = np.std(data)
            cv = std / mean
            data_range = np.max(data) - np.min(data)
            rel_diff = (data_range / mean) * 100
            wiwnu_3sigma = (3 * std / mean) * 100
            results.append({
                "Wafer": wafer,
                "Mean": mean,
                "Std": std,
                "CV": cv,
                "Range": data_range,
                "Rel Diff (%)": rel_diff,
                "WIWNU (3σ %)": wiwnu_3sigma
            })
        else:
            results.append({
                "Wafer": wafer,
                "Mean": np.nan,"Std": np.nan,"CV": np.nan,"Range": np.nan,"Rel Diff (%)": np.nan,"WIWNU (3σ %)": np.nan
            })

    st.subheader("Uniformity Metrics Per Wafer")
    st.dataframe(pd.DataFrame(results).set_index('Wafer'))
    

    st.subheader("Overlayed Polish Profile: All Wafers")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = plt.cm.tab20.colors  # up to 20 unique colors
    
    for idx, wafer in enumerate(wafer_names):
        row = polish_profile_data.loc[wafer]
        y = pd.to_numeric(row, errors='coerce').values
        x = np.array(positions)
        valid = ~np.isnan(y)
        if np.any(valid):
            ax.scatter(x[valid], y[valid], s=18, label=wafer, color=colors[idx % len(colors)], alpha=0.7)
    
    ax.set_xlabel("Position (mm)")
    ax.set_ylabel("Polish Rate (Å/min)")
    ax.set_title("Polish Profile Across All Wafers")
    ax.legend(title="Wafer", bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.set_ylim(bottom=0)  # <-- Set Y-axis to start from 0
    st.pyplot(fig)


    ### --- Tunability calculation per zone ---
    # Map profile positions to zones
    # Your zone boundaries: e.g. 0-25, 25-52, ...
    zone_bounds = [
        ('A1', 0, 25),
        ('A2', 25, 52),
        ('A3', 52, 78),
        ('A4', 78, 105),
        ('A5', 105, 123),
        ('A6', 123, 133),
        ('A7', 133, 142),
        ('A8', 142, 150)
    ]

    # Helper function to assign position to zone
    def pos_to_zone(pos):
        abs_pos = abs(pos)
        for zone, start, end in zone_bounds:
            if start <= abs_pos < end:
                return zone
        return None

    
    # ------ Prepare tunability/plot results ------
    tunability_row = []
    plot_row = []
    fullsize_buffers = []
    
    for zone in zone_names:
        zone_mean_rates = []
        zone_pressures = []
        for wafer in wafer_names:
            p = zone_pressure_data.loc[wafer, zone]
            row = polish_profile_data.loc[wafer]
            idxs = [i for i, pos in enumerate(positions) if pos_to_zone(pos) == zone]
            data = pd.to_numeric(row, errors='coerce').dropna().values
            zone_data = [data[i] for i in range(len(data)) if i in idxs]
            if len(zone_data) > 0 and p != '':
                zone_mean_rates.append(np.mean(zone_data))
                try:
                    zone_pressures.append(float(p))
                except:
                    continue
    
        # Tunability (slope)
        if len(zone_mean_rates) > 1 and len(zone_mean_rates) == len(zone_pressures):
            m, c = np.polyfit(zone_pressures, zone_mean_rates, 1)
            tunability_row.append(m)
        else:
            tunability_row.append(0.0)
    
        # --- Mini Plot ---
        mini_fig, mini_ax = plt.subplots(figsize=(1.8, 1.2))
        if len(zone_mean_rates) > 1:
            mini_ax.scatter(zone_pressures, zone_mean_rates, s=12)
            x_fit = np.array(zone_pressures)
            y_fit = m * x_fit + c
            mini_ax.plot(x_fit, y_fit, 'k:', linewidth=1)
        mini_ax.axis('off')
        plt.tight_layout(pad=0)
        mini_buf = io.BytesIO()
        mini_fig.savefig(mini_buf, format="png")
        mini_buf.seek(0)
        plt.close(mini_fig)
        plot_row.append(mini_buf)
    
        # --- Full-size Plot ---
        full_fig, full_ax = plt.subplots(figsize=(5, 3.5))
        if len(zone_mean_rates) > 1:
            full_ax.scatter(zone_pressures, zone_mean_rates, s=30, color='tab:blue')
            x_fit = np.array(zone_pressures)
            y_fit = m * x_fit + c
            full_ax.plot(x_fit, y_fit, 'k:', linestyle=':', linewidth=1.5)
        full_ax.set_title(f"Zone {zone}: Rate vs Pressure")
        full_ax.set_xlabel("Pressure (hPa)")
        full_ax.set_ylabel("Mean Polish Rate (Å/min)")
        plt.tight_layout()
        full_buf = io.BytesIO()
        full_fig.savefig(full_buf, format="png")
        full_buf.seek(0)
        plt.close(full_fig)
        fullsize_buffers.append(full_buf)
    
    # ---- Display Table With Clickable Plots ----
    st.subheader("Tunability Per Zone")
    cols = st.columns(len(zone_names))
    
    for col_idx, col in enumerate(cols):
        zone = zone_names[col_idx]
        with col:
            st.write(f"**{zone}**")
            st.write(f"Tunability: `{tunability_row[col_idx]:.3f}`")
            st.image(plot_row[col_idx], width=60)
            with st.expander("Enlarge Plot"):
                st.image(fullsize_buffers[col_idx], use_container_width=True)
            
            
        
    