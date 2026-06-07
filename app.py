import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from datetime import datetime

# =====================================================================
# 1. PAGE SETUP & CYBERPUNK CSS ARCHITECTURE
# =====================================================================
st.set_page_config(
    page_title="DrillSense Pro v2.0.1",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom injection for dark neon engineering style
st.markdown("""
    <style>
    /* Main body background override */
    .stApp {
        background-color: #0B0F13 !important;
        color: #E2E8F0 !important;
    }
    
    /* Custom Neon Containers */
    .panel-box {
        background: rgba(16, 22, 30, 0.85);
        border: 1px solid #1E293B;
        border-radius: 6px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
    }
    .panel-header {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #64748B;
        margin-bottom: 10px;
        border-bottom: 1px solid #1E293B;
        padding-bottom: 4px;
    }
    
    /* Twin/Telemetry Metric Blocks */
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        font-family: 'Courier New', monospace;
        color: #00F0FF;
    }
    .metric-unit {
        font-size: 0.75rem;
        color: #64748B;
        margin-left: 4px;
    }
    
    /* Dynamic Status Badges */
    .badge-nominal {
        background-color: rgba(16, 185, 129, 0.1);
        color: #10B981;
        border: 1px solid #10B981;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .badge-warning {
        background-color: rgba(245, 158, 11, 0.1);
        color: #F59E0B;
        border: 1px solid #F59E0B;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .badge-critical {
        background-color: rgba(239, 68, 68, 0.1);
        color: #EF4444;
        border: 1px solid #EF4444;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    /* Code blocks adjustments */
    code {
        color: #F43F5E !important;
        background-color: #1E293B !important;
    }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 2. SESSION STATE STATE-MACHINE INITIALIZATION
# =====================================================================
if 'running' not in st.session_state:
    st.session_state.running = False
if 'mode' not in st.session_state:
    st.session_state.mode = "MANUAL"
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=[
        'Timestamp', 'Temperature', 'Vibration', 'Spindle_Speed', 'Torque', 'Pressure', 'Tool_Wear', 'Failure_Prob'
    ])
if 'log' not in st.session_state:
    st.session_state.log = ["SYSTEM INITIALIZED - STANDBY"]

# =====================================================================
# 3. CORE TELEMETRY SIMULATION ENGINE
# =====================================================================
def get_sensor_packet():
    t_str = datetime.now().strftime("%H:%M:%S")
    
    if st.session_state.running:
        # Generate operational data paths mimicking mechanical loading
        base_time = (time.time() % 300) / 3
        
        # Introduce a sudden anomaly surge at specific intervals to match video demonstration
        is_anomaly = (int(time.time()) % 45 > 35)
        
        if is_anomaly:
            vibration = np.random.normal(6.2, 0.5)
            temperature = np.random.normal(84.5, 2.1)
            torque = np.random.normal(48.0, 3.0)
            pressure = np.random.normal(210.0, 12.0)
            failure_prob = np.random.uniform(52.0, 78.4)
        else:
            vibration = np.random.normal(1.8, 0.15)
            temperature = np.random.normal(42.1, 0.8)
            torque = np.random.normal(12.5, 0.4)
            pressure = np.random.normal(114.2, 2.5)
            failure_prob = np.random.uniform(3.1, 8.2)
            
        spindle_speed = int(np.random.normal(1750, 25) if not is_anomaly else np.random.normal(1350, 90))
        tool_wear = round(min(100.0, 12.4 + (base_time * 0.15)), 2)
    else:
        # Machine Standby state values
        vibration, temperature, torque, pressure, failure_prob, spindle_speed, tool_wear = 0.0, 21.0, 0.0, 0.0, 0.0, 0, 12.4
        
    return {
        'Timestamp': t_str, 'Temperature': round(temperature, 1), 'Vibration': round(vibration, 2),
        'Spindle_Speed': spindle_speed, 'Torque': round(torque, 1), 'Pressure': round(pressure, 1),
        'Tool_Wear': tool_wear, 'Failure_Prob': round(failure_prob, 1)
    }

# Update real-time loop variables
current_packet = get_sensor_packet()
if st.session_state.running:
    st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([current_packet])]).tail(30)
    
    # Process system logs dynamically based on thresholds
    if current_packet['Failure_Prob'] > 50.0:
        log_entry = f"[{current_packet['Timestamp']}] CRITICAL: HIGH RISK FAILURE FAULT STAGE DETECTED"
        if log_entry not in st.session_state.log:
            st.session_state.log.insert(0, log_entry)

df_history = st.session_state.history

# =====================================================================
# 4. MASTER NAVIGATION HEADER
# =====================================================================
h_col1, h_col2, h_col3 = st.columns([0.4, 0.4, 0.2])
with h_col1:
    st.markdown("<h2 style='margin:0; padding:0; color:#FFFFFF;'>⚙️ DRILLSENSE PRO <span style='font-size:0.9rem; color:#64748B;'>v2.0.1</span></h2>", unsafe_allow_html=True)
with h_col2:
    status_badge = '<span class="badge-nominal">NOMINAL</span>' if current_packet['Failure_Prob'] < 50.0 else '<span class="badge-critical">CRITICAL ALERT</span>'
    st.markdown(f"<div style='padding-top:12px;'>DATASET: 10,000 ROWS &nbsp;&nbsp;|&nbsp;&nbsp; STATUS: {status_badge}</div>", unsafe_allow_html=True)
with h_col3:
    st.markdown(f"<div style='text-align:right; padding-top:12px; color:#64748B; font-family:monospace;'>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>", unsafe_allow_html=True)

# Application Navigation Tabs
tab_live, tab_analytics, tab_ml, tab_matlab = st.tabs([
    "📊 LIVE MONITOR", "📈 ANALYTICS", "🤖 ML MODEL", "🛠️ MATLAB GUIDE"
])

# =====================================================================
# TAB 1: LIVE TELEMETRY & DIGITAL TWIN MONITORING
# =====================================================================
with tab_live:
    layout_left, layout_right = st.columns([0.3, 0.7])
    
    with layout_left:
        st.markdown("<div class='panel-box'><div class='panel-header'>VIRTUAL DRILL UNIT - REAL-TIME TWIN</div>", unsafe_allow_html=True)
        
        # Engine Control Systems UI Panel
        c1, c2 = st.columns(2)
        with c1:
            if st.button("▶ START" if not st.session_state.running else "⏸ STOP", use_container_width=True):
                st.session_state.running = not st.session_state.running
                st.session_state.log.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] USER INTERACTION: TOGGLE STATE")
                st.rerun()
        with c2:
            if st.button(f"🔄 {st.session_state.mode}", use_container_width=True):
                st.session_state.mode = "AUTO" if st.session_state.mode == "MANUAL" else "MANUAL"
                st.rerun()
                
        st.markdown(f"""
            <div style="text-align:center; padding:30px 0;">
                <div style="font-size:4rem; color:{'#10B981' if st.session_state.running else '#64748B'};">🌀</div>
                <div class="metric-value">{current_packet['Spindle_Speed']}<span class="metric-unit">RPM</span></div>
                <div style="color:#64748B; font-size:0.8rem; margin-top:5px;">SPINDLE MOTOR VELOCITY</div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Real-time System Alert Log Display
        st.markdown("<div class='panel-box'><div class='panel-header'>⚠️ SYSTEM ALERT LOGS</div>", unsafe_allow_html=True)
        for entry in st.session_state.log[:4]:
            st.markdown(f"<p style='font-family:monospace; font-size:0.75rem; color:#EF4444; margin:2px 0;'>{entry}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with layout_right:
        st.markdown("<div class='panel-box'><div class='panel-header'>PROBABILISTIC FAILURE FORECAST</div>", unsafe_allow_html=True)
        prob_val = current_packet['Failure_Prob']
        color_hex = "#EF4444" if prob_val > 50.0 else ("#F59E0B" if prob_val > 30.0 else "#10B981")
        st.markdown(f"<div style='font-size:2.5rem; font-weight:bold; font-family:monospace; color:{color_hex};'>{prob_val}%</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 3x2 Matrix Grid for Secondary High-Density Sensor Parameters
        st.markdown("<div class='panel-box'><div class='panel-header'>LIVE REAL-TIME TELEMETRY MATRIX</div>", unsafe_allow_html=True)
        m_col1, m_col2, m_col3 = st.columns(3)
        
        with m_col1:
            st.markdown(f"<div><span style='color:#64748B; font-size:0.8rem;'>VIBRATION</span><br><span class='metric-value'>{current_packet['Vibration']}</span><span class='metric-unit'>mm/s</span></div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"<div><span style='color:#64748B; font-size:0.8rem;'>TEMPERATURE</span><br><span class='metric-value'>{current_packet['Temperature']}</span><span class='metric-unit'>°C</span></div>", unsafe_allow_html=True)
            
        with m_col2:
            st.markdown(f"<div><span style='color:#64748B; font-size:0.8rem;'>TORQUE</span><br><span class='metric-value'>{current_packet['Torque']}</span><span class='metric-unit'>Nm</span></div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"<div><span style='color:#64748B; font-size:0.8rem;'>PRESSURE</span><br><span class='metric-value'>{current_packet['Pressure']}</span><span class='metric-unit'>bar</span></div>", unsafe_allow_html=True)
            
        with m_col3:
            st.markdown(f"<div><span style='color:#64748B; font-size:0.8rem;'>TOOL WEAR PROFILE</span><br><span class='metric-value'>{current_packet['Tool_Wear']}%</span></div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"<div><span style='color:#64748B; font-size:0.8rem;'>SAMPLING FREQUENCY</span><br><span class='metric-value'>2.4</span><span class='metric-unit'>kHz</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Sparklines / Time-Series Telemetry Sub-plots
        st.markdown("<div class='panel-box'><div class='panel-header'>TREND TIMELINE - PREDICTOR OVERLAYS</div>", unsafe_allow_html=True)
        if not df_history.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_history['Timestamp'], y=df_history['Temperature'], name="Temp (°C)", line=dict(color='#FF4B4B', width=2)))
            fig.add_trace(go.Scatter(x=df_history['Timestamp'], y=df_history['Vibration'] * 10, name="Vibration x10 (mm/s)", line=dict(color='#00F0FF', width=2)))
            fig.add_trace(go.Scatter(x=df_history['Timestamp'], y=df_history['Failure_Prob'], name="Risk %", line=dict(color='#F59E0B', width=1, dash='dot')))
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=10, b=10),
                height=180,
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#1E293B')
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("System on Standby. Toggle 'START' engine to initialize visualization stream pipelines.")
        st.markdown("</div>", unsafe_allow_html=True)

# =====================================================================
# TAB 2: EXPLORATORY ANOMALY DATA ANALYTICS
# =====================================================================
with tab_analytics:
    st.markdown("<div class='panel-box'><div class='panel-header'>HISTORICAL DATASET STATISTICAL OVERVIEW (10,000 DRILL CYCLES)</div>", unsafe_allow_html=True)
    
    # Static mockup dataset summary to mirror the analytical view in video 1
    mock_summary = pd.DataFrame({
        'Feature Metric': ['Temperature', 'Vibration', 'Spindle Speed', 'Torque', 'Tool Wear'],
        'Min Bounds': [32.4, 0.12, 850, 2.1, 0.0],
        'Max Bounds': [98.6, 8.41, 2400, 64.2, 100.0],
        'Mean Avg': [54.2, 2.15, 1642, 18.4, 42.1],
        'Failure Correlation': ['84.2%', '91.5%', '-45.1%', '76.8%', '89.1%']
    })
    st.table(mock_summary)
    st.markdown("</div>", unsafe_allow_html=True)
    
    an_col1, an_col2 = st.columns(2)
    with an_col1:
        st.markdown("<div class='panel-box'><div class='panel-header'>WEAR REGIME FREQUENCY DISTRIBUTION</div>", unsafe_allow_html=True)
        # Mocking categorical distribution charts
        wear_labels = ['0-25 μm (New)', '25-100 μm (Normal)', '100-200 μm (Warning)', '>200 μm (Critical Fault)']
        wear_values = [1200, 6800, 1500, 500]
        fig_pie = go.Figure(data=[go.Pie(labels=wear_labels, values=wear_values, hole=.4, marker=dict(colors=['#10B981','#3B82F6','#F59E0B','#EF4444']))])
        fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=10, b=10), height=240)
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with an_col2:
        st.markdown("<div class='panel-box'><div class='panel-header'>TORQUE VS SPINDLE VELOCITY CLUSTERING DESIGNS</div>", unsafe_allow_html=True)
        # Scatter layout cluster visualization
        np.random.seed(42)
        mock_rpm = np.random.normal(1600, 300, 200)
        mock_trq = 100000 / (mock_rpm + 1) + np.random.normal(10, 3, 200)
        fig_scatter = go.Figure(data=go.Scatter(x=mock_rpm, y=mock_trq, mode='markers', marker=dict(color='#00F0FF', opacity=0.6)))
        fig_scatter.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=10, b=10), height=240)
        st.plotly_chart(fig_scatter, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# =====================================================================
# TAB 3: MACHINE LEARNING EVALUATION METRICS
# =====================================================================
with tab_ml:
    ml_col1, ml_col2 = st.columns([0.3, 0.7])
    
    with ml_col1:
        st.markdown("<div class='panel-box'><div class='panel-header'>MODEL VALIDATION METRICS</div>", unsafe_allow_html=True)
        st.markdown("""
            <div style='margin-bottom:15px;'>
                <span style='color:#64748B; font-size:0.75rem;'>CLASSIFICATION ACCURACY</span><br>
                <span style='font-size:2rem; font-weight:bold; color:#10B981;'>99.5%</span>
            </div>
            <div style='margin-bottom:15px;'>
                <span style='color:#64748B; font-size:0.75rem;'>PRECISION METRIC SCORE</span><br>
                <span style='font-size:2rem; font-weight:bold; color:#00F0FF;'>100.0%</span>
            </div>
            <div style='margin-bottom:15px;'>
                <span style='color:#64748B; font-size:0.75rem;'>MODEL SENSITIVITY (RECALL)</span><br>
                <span style='font-size:2rem; font-weight:bold; color:#F59E0B;'>97.1%</span>
            </div>
            <div>
                <span style='color:#64748B; font-size:0.75rem;'>F1 CONFIDENCE SCORE</span><br>
                <span style='font-size:2rem; font-weight:bold; color:#10B981;'>98.6%</span>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with ml_col2:
        st.markdown("<div class='panel-box'><div class='panel-header'>FEATURE IMPORTANCE SHAP RANKINGS</div>", unsafe_allow_html=True)
        features = ['Vibration RMS', 'Torque Elasticity', 'Spindle Delta', 'Chamber Heat', 'Tool Wear Index']
        importance = [0.427, 0.218, 0.161, 0.124, 0.070]
        fig_bar = go.Figure(go.Bar(x=importance, y=features, orientation='h', marker_color='#3B82F6'))
        fig_bar.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=10, b=10), height=230)
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# =====================================================================
# TAB 4: INTER-OPERABLE MATLAB PIPELINE INTEGRATION GUIDE
# =====================================================================
with tab_matlab:
    st.markdown("<div class='panel-box'><div class='panel-header'>PRODUCTION IMPLEMENTATION METHODS AND CONNECTOR SCRIPTS</div>", unsafe_allow_html=True)
    
    m_method = st.radio("Select Interface Pipeline Architecture:", [
        "Method 1: CSV Bulk Batch Pipeline Engine", 
        "Method 2: Real-time MATLAB Python Engine Core",
        "Method 3: Distributed TCP/IP Streaming Sockets"
    ])
    
    st.markdown("---")
    
    if "Method 1" in m_method:
        st.subheader("Data Export Pipeline Implementation (MATLAB ➡️ Streamlit)")
        st.code("""
% MATLAB Telemetry Serialization Script
% Purpose: Dump physical streaming data matrix arrays to disk
data_matrix = [temperature_vector, vibration_vector, speed_vector, torque_vector];
csv_headers = {'Temperature', 'Vibration', 'Spindle_Speed', 'Torque'};

output_table = array2table(data_matrix, 'VariableNames', csv_headers);
writetable(output_table, 'drill_sensor_data.csv');
disp('Telemetry frame matrices successfully synced.');
        """, language="matlab")
        
    elif "Method 2" in m_method:
        st.subheader("Live Process Model Mapping via Python Engine APIs")
        st.code("""
# Python execution terminal calling native MATLAB compiled runtimes
import matlab.engine

eng = matlab.engine.start_matlab()
# Execute failure classification network weights directly inside original matrix workspaces
failure_probability = eng.predict_cnc_fault(float(vibration), float(temperature))
print(f"MATLAB Execution Predicted Health Matrix Index: {failure_probability}%")
        """, language="python")
        
    else:
        st.subheader("High Frequency Low-Latency Streaming Configuration via TCP/IP")
        st.code("""
% MATLAB Send Socket Configuration
t_client = tcpclient('127.0.0.1', 5005);
while true
    sensor_packet = [vibration_value, temperature_value, torque_value];
    write(t_client, sensor_packet, "double");
    pause(0.01); % Stream at steady 100Hz pipelines
end
        """, language="matlab")
    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================================
# 5. HIGH-FREQUENCY INTERACTION LOOP MECHANISM
# =====================================================================
if st.session_state.running:
    time.sleep(0.8) # Set sample clock cycle refresh rate latency
    st.rerun()
        
