import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from datetime import datetime

# =====================================================================
# 1. PAGE CONFIGURATION & CYBERPUNK UI STYLING
# =====================================================================
st.set_page_config(
    page_title="DrillSense Pro v2.0.1",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dark-cyberpunk layout stylesheet injection
st.markdown("""
    <style>
    .stApp {
        background-color: #0A0D10 !important;
        color: #E2E8F0 !important;
    }
    /* Dashboard Glassmorphism Cards */
    .panel-card {
        background: rgba(16, 22, 30, 0.9);
        border: 1px solid #1E293B;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.6);
    }
    .panel-title {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #64748B;
        margin-bottom: 12px;
        border-bottom: 1px solid #1E293B;
        padding-bottom: 6px;
    }
    /* High-Density Matrix Grid Items */
    .matrix-box {
        background: #11161F;
        border: 1px solid #1E293B;
        border-radius: 6px;
        padding: 12px;
        text-align: center;
    }
    .matrix-label {
        font-size: 0.7rem;
        color: #64748B;
        font-weight: 600;
        letter-spacing: 0.05em;
    }
    .matrix-value {
        font-size: 1.5rem;
        font-weight: 700;
        font-family: 'Courier New', monospace;
        color: #00F0FF;
        margin-top: 4px;
    }
    .matrix-unit {
        font-size: 0.75rem;
        color: #475569;
        margin-left: 2px;
    }
    /* Status Labels */
    .status-active { color: #10B981; font-weight: bold; }
    .status-alert { color: #EF4444; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 2. STATE MACHINE LOGIC (SESSION STATE)
# =====================================================================
if 'running' not in st.session_state:
    st.session_state.running = False
if 'mode' not in st.session_state:
    st.session_state.mode = "MANUAL"
if 'horizon' not in st.session_state:
    st.session_state.horizon = 10
if 'history' not in st.session_state:
    # Initialize baseline metrics dataframe
    st.session_state.history = pd.DataFrame({
        'Timestamp': [datetime.now().strftime("%H:%M:%S")], 
        'Temperature': [42.0], 'Vibration': [1.5], 'Spindle_Speed': [1750], 
        'Torque': [12.5], 'Pressure': [114.0], 'Tool_Wear': [12.4], 'Failure_Prob': [4.2]
    })
if 'logs' not in st.session_state:
    st.session_state.logs = ["SYSTEM READY - STANDBY MODE"]

# =====================================================================
# 3. ADVANCED SIGNAL PROCESSING ENGINE
# =====================================================================
def compute_telemetry_step():
    t_now = datetime.now().strftime("%H:%M:%S")
    if not st.session_state.running:
        return {
            'Timestamp': t_now, 'Temperature': 22.1, 'Vibration': 0.02, 
            'Spindle_Speed': 0, 'Torque': 0.0, 'Pressure': 0.0, 
            'Tool_Wear': 12.4, 'Failure_Prob': 0.0
        }
    
    # Mathematical data degradation sim over time
    elapsed_factor = (time.time() % 400) / 4
    cycle_spike = (int(time.time()) % 30 > 22) # Generates automated cyclical load faults
    
    if cycle_spike:
        vib = np.random.normal(5.8, 0.4)
        tmp = np.random.normal(81.2, 1.8)
        trq = np.random.normal(44.1, 2.5)
        prs = np.random.normal(208.5, 9.0)
        fail_p = min(99.4, 55.0 + (elapsed_factor * 0.2))
        spd = int(np.random.normal(1320, 45))
    else:
        vib = np.random.normal(1.6, 0.1)
        tmp = np.random.normal(41.5, 0.6)
        trq = np.random.normal(12.2, 0.3)
        prs = np.random.normal(112.4, 1.5)
        fail_p = max(2.1, 3.5 + (elapsed_factor * 0.05))
        spd = int(np.random.normal(1765, 15))

    wear = round(min(100.0, 12.4 + (elapsed_factor * 0.08)), 2)
    
    return {
        'Timestamp': t_now, 'Temperature': round(tmp, 1), 'Vibration': round(vib, 2),
        'Spindle_Speed': spd, 'Torque': round(trq, 1), 'Pressure': round(prs, 1),
        'Tool_Wear': wear, 'Failure_Prob': round(fail_p, 1)
    }

# Process mathematical pipeline state updates
pkt = compute_telemetry_step()
if st.session_state.running:
    st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([pkt])]).tail(25)
    if pkt['Failure_Prob'] > 50.0:
        msg = f"[{pkt['Timestamp']}] CRITICAL FAULT LEVEL RECORDED: HAZARD THRESHOLD EXCEEDED"
        if msg not in st.session_state.logs:
            st.session_state.logs.insert(0, msg)

hist_df = st.session_state.history

# =====================================================================
# 4. DASHBOARD HEADER PLATFORM
# =====================================================================
h_1, h_2, h_3 = st.columns([0.3, 0.5, 0.2])
with h_1:
    st.markdown("<h2 style='margin:0; color:#FFFFFF;'>⚙️ DRILLSENSE PRO <span style='font-size:0.85rem; color:#475569;'>v2.0.1</span></h2>", unsafe_allow_html=True)
with h_2:
    badge = '<span class="status-active" style="border:1px solid #10B981; padding:2px 8px; background:rgba(16,185,129,0.1); border-radius:4px;">NOMINAL OPERATION</span>' if pkt['Failure_Prob'] < 50.0 else '<span class="status-alert" style="border:1px solid #EF4444; padding:2px 8px; background:rgba(239,68,68,0.1); border-radius:4px;">CRITICAL SYSTEM FAULT</span>'
    st.markdown(f"<div style='padding-top:8px;'>DATA STREAM: ACTIVE (10k ROWS) &nbsp;&nbsp;|&nbsp;&nbsp; MACHINE STATUS: {badge}</div>", unsafe_allow_html=True)
with h_3:
    st.markdown(f"<div style='text-align:right; font-family:monospace; color:#475569; padding-top:8px;'>{datetime.now().strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)

tab_monitor, tab_analytics, tab_ml, tab_matlab = st.tabs([
    "🎯 LIVE MONITOR", "📊 ANALYTICS VIEW", "🧠 ML HORIZON MODEL", "💻 MATLAB INTERFACE"
])

# =====================================================================
# TAB 1: LIVE HARDWARE TWIN & SENSOR TELEMETRY METRIC MATRIX
# =====================================================================
with tab_monitor:
    col_left, col_right = st.columns([0.3, 0.7])
    
    with col_left:
        st.markdown("<div class='panel-card'><div class='panel-title'>Virtual Drill Twin Control</div>", unsafe_allow_html=True)
        # Action execution inputs
        btn_1, btn_2 = st.columns(2)
        with btn_1:
            if st.button("▶ START" if not st.session_state.running else "⏸ STOP", use_container_width=True):
                st.session_state.running = not st.session_state.running
                st.rerun()
        with btn_2:
            if st.button(f"⚙️ {st.session_state.mode}", use_container_width=True):
                st.session_state.mode = "AUTO" if st.session_state.mode == "MANUAL" else "MANUAL"
                st.rerun()
                
        # Simulated rotational twin element
        st.markdown(f"""
            <div style='text-align:center; padding:35px 0;'>
                <div style='font-size:3.5rem; color:{'#00F0FF' if st.session_state.running else '#334155'}; animation: spin 2s linear infinite;'>🌀</div>
                <div style='font-size:1.8rem; font-weight:700; font-family:monospace; color:#FFFFFF; margin-top:10px;'>{pkt['Spindle_Speed']}<span style='font-size:0.8rem; color:#475569;'> RPM</span></div>
                <div style='font-size:0.7rem; color:#475569; letter-spacing:0.05em;'>SPINDLE VELOCITY ROTATION TRACKER</div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Real-time event logging
        st.markdown("<div class='panel-card'><div class='panel-title'>Active Alert Stream Logs</div>", unsafe_allow_html=True)
        for log in st.session_state.logs[:4]:
            st.markdown(f"<p style='font-family:monospace; font-size:0.7rem; color:#F43F5E; margin:3px 0;'>{log}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        # High Density 3x2 Matrix Setup
        st.markdown("<div class='panel-card'><div class='panel-title'>High-Density Realtime Sensor Matrix</div>", unsafe_allow_html=True)
        g_1, g_2, g_3 = st.columns(3)
        with g_1:
            st.markdown(f"<div class='matrix-box'><div class='matrix-label'>🛢️ OIL RATE</div><div class='matrix-value'>44<span class='matrix-unit'>%</span></div></div>", unsafe_allow_html=True)
            st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='matrix-box'><div class='matrix-label'>🌡️ SPINDLE HEAT</div><div class='matrix-value'>{pkt['Temperature']}<span class='matrix-unit'>°C</span></div></div>", unsafe_allow_html=True)
        with g_2:
            st.markdown(f"<div class='matrix-box'><div class='matrix-label'>⏳ TOOL WEAR</div><div class='matrix-value'>{pkt['Tool_Wear']}<span class='matrix-unit'>%</span></div></div>", unsafe_allow_html=True)
            st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='matrix-box'><div class='matrix-label'>📳 VIBRATION RMS</div><div class='matrix-value'>{pkt['Vibration']}<span class='matrix-unit'>mm/s</span></div></div>", unsafe_allow_html=True)
        with g_3:
            st.markdown(f"<div class='matrix-box'><div class='matrix-label'>⚡ ACCELERATION</div><div class='matrix-value'>1.85<span class='matrix-unit'>G</span></div></div>", unsafe_allow_html=True)
            st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='matrix-box'><div class='matrix-label'>🔮 RISK PROBABILITY</div><div class='matrix-value' style='color:#EF4444;'>{pkt['Failure_Prob']}<span class='matrix-unit'>%</span></div></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Micro timelines 
        st.markdown("<div class='panel-card'><div class='panel-title'>Realtime Metric Waveforms</div>", unsafe_allow_html=True)
        if st.session_state.running:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist_df['Timestamp'], y=hist_df['Temperature'], name="Temp (°C)", line=dict(color='#EF4444', width=2)))
            fig.add_trace(go.Scatter(x=hist_df['Timestamp'], y=hist_df['Vibration'] * 12, name="Vibration (Scaled)", line=dict(color='#00F0FF', width=2)))
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10,r=10,t=10,b=10), height=160, xaxis=dict(showgrid=False))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("System idling. Engage the 'START' hardware toggle switch to pipe incoming live telemetry matrices.")
        st.markdown("</div>", unsafe_allow_html=True)

# =====================================================================
# TAB 2: ANALYTICS PREDICTIVE HAZARD AREAS
# =====================================================================
with tab_analytics:
    st.markdown("<div class='panel-card'><div class='panel-title'>Machine Run Summary Metrics</div>", unsafe_allow_html=True)
    an_df = pd.DataFrame({
        'Telemetry Variable': ['Temperature Sensor', 'Vibration Matrix', 'Rotational Velocity', 'Torque Stress Load'],
        'Operational Min': [31.5, 0.08, 920, 1.8],
        'Operational Max': [94.2, 7.85, 2350, 61.4],
        'Calculated Median': [51.4, 2.04, 1624, 16.2],
        'System Weight Value': ['84.1%', '92.4%', '41.5%', '79.2%']
    })
    st.table(an_df)
    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================================
# TAB 3: STEPWISE FORECAST REGIMES (COMBINED FROM MATLAB VIDEO)
# =====================================================================
with tab_ml:
    st.markdown("<div class='panel-card'><div class='panel-title'>Stepwise Horizon Predictive Machine Learning</div>", unsafe_allow_html=True)
    
    # Matching the Stepwise Horizon Slider from video 3
    st.session_state.horizon = st.select_slider("Select Stepwise Prediction Horizon Steps:", options=[5, 10, 15], value=st.session_state.horizon)
    
    h_col1, h_col2 = st.columns([0.7, 0.3])
    with h_col1:
        # Build multi step forecasting visualization path
        x_steps = [f"T + {i}" for i in range(1, st.session_state.horizon + 1)]
        
        # Smooth wave logic trajectory
        y_vals = [float(pkt['Failure_Prob']) + (np.sin(i/2) * 5) + (i * 1.2) for i in range(1, st.session_state.horizon + 1)]
        
        fig_step = go.Figure()
        fig_step.add_trace(go.Scatter(x=x_steps, y=y_vals, mode='lines+markers', name='Predictive Trend Line', line=dict(color='#00F0FF', width=3)))
        fig_step.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=250, margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig_step, use_container_width=True)
        
    with h_col2:
        st.markdown("<p style='color:#64748B; font-size:0.75rem; font-weight:bold;'>ESTIMATED HORIZON TARGET VALUES</p>", unsafe_allow_html=True)
        forecast_records = pd.DataFrame({
            'Step Step': x_steps,
            'Failure Risk %': [f"{round(min(100.0, y), 1)}%" for y in y_vals]
        })
        st.dataframe(forecast_records, use_container_width=True, height=220)
    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================================
# TAB 4: PRODUCTION COMPILED MATLAB WORKFLOW SCRIPTS
# =====================================================================
with tab_matlab:
    st.markdown("<div class='panel-card'><div class='panel-title'>Compiled Production Pipelines</div>", unsafe_allow_html=True)
    st.subheader("High Frequency Core Processing Logic Loop")
    st.code("""
% MATLAB Core Low-Latency Processing & Matrix Transformation Script
% Initialize programmatic sockets to intercept machine telemetry matrices
t_socket = tcpclient('127.0.0.1', 5005);

while true
    if t_socket.BytesAvailable > 0
        raw_matrix = read(t_socket, t_socket.BytesAvailable, "double");
        
        % Normalize array parameters using validation logic
        normalized_temp = (raw_matrix(1) - 20) / (100 - 20);
        normalized_vibe = raw_matrix(2) / 10.0;
        
        fprintf('Processing System Arrays -- Temperature: %f, Vibration: %f\\n', normalized_temp, normalized_vibe);
    end
    pause(0.1);
end
    """, language="matlab")
    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================================
# 5. HIGH REFRESH RATE EXECUTION LATENCY TIMING
# =====================================================================
if st.session_state.running:
    time.sleep(0.6) # High-speed operational polling loop delay clock
    st.rerun()

        
