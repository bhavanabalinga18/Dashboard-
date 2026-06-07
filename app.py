import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="DrillSense Pro | CNC Analytics",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Mode/Custom Styling
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .metric-box {
        background-color: #1f2937;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #374151;
        text-align: center;
    }
    .status-normal { color: #10B981; font-weight: bold; }
    .status-warning { color: #F59E0B; font-weight: bold; }
    .status-danger { color: #EF4444; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# App Header
st.title("⚙️ DrillSense Pro")
st.subheader("Real-Time CNC Failure Prediction & Telemetry Dashboard")
st.markdown("---")

# Sidebar Configuration
st.sidebar.header("🕹️ Control Panel & Settings")
machine_id = st.sidebar.selectbox("Select Machine Unit", ["CNC-Milling-01", "CNC-Milling-02", "CNC-Lathe-05"])
sampling_rate = st.sidebar.slider("Data Refresh Rate (seconds)", 0.5, 3.0, 1.0)
anomaly_threshold = st.sidebar.slider("Failure Threshold (%)", 50, 95, 80)

# Initialize Session State for Historical Data
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=[
        'Timestamp', 'Temperature', 'Vibration', 'Spindle_Speed', 'Tool_Wear', 'Failure_Prob'
    ])

# ----------------- SIMULATED REAL-TIME DATA ENGINE -----------------
def generate_live_data():
    t = datetime.now().strftime("%H:%M:%S")
    
    # Injecting random patterns with occasional simulated spikes/wear
    base_wear = (time.time() % 300) / 3 # Tool wear gradually builds up over 5 mins
    temp = np.random.normal(65, 3) + (base_wear * 0.2)
    vibration = np.random.normal(1.5, 0.2) + (np.random.choice([0, 2.5], p=[0.95, 0.05]) if base_wear > 50 else 0)
    spindle = np.random.normal(12000, 150)
    
    # Predictive heuristic algorithm for RUL / Failure Risk
    failure_prob = min(99.9, (base_wear * 0.5) + (max(0, temp - 65) * 2) + (max(0, vibration - 1.5) * 15))
    
    return {
        'Timestamp': t, 'Temperature': round(temp, 1), 'Vibration': round(vibration, 2),
        'Spindle_Speed': int(spindle), 'Tool_Wear': round(base_wear, 1), 'Failure_Prob': round(failure_prob, 1)
    }

# Fetch new data point
new_data = generate_live_data()
# Append to session state history (Keep last 20 records for live chart)
st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([new_data])]).tail(20)
df = st.session_state.history

# ----------------- LIVE METRICS COUNTERS -----------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    prob = new_data['Failure_Prob']
    if prob < 40:
        status_html = f"<span class='status-normal'>HEALTHY ({prob}%)</span>"
    elif prob < anomaly_threshold:
        status_html = f"<span class='status-warning'>ATTENTION ({prob}%)</span>"
    else:
        status_html = f"<span class='status-danger'>CRITICAL ({prob}%)</span>"
        
    st.markdown(f"<div class='metric-box'><h4>🔮 Failure Probability</h4><h2>{status_html}</h2></div>", unsafe_allow_html=True)

with col2:
    st.markdown(f"<div class='metric-box'><h4>🌡️ Spindle Temp</h4><h2>{new_data['Temperature']} °C</h2></div>", unsafe_allow_html=True)

with col3:
    st.markdown(f"<div class='metric-box'><h4>📳 Vibration (RMS)</h4><h2>{new_data['Vibration']} mm/s</h2></div>", unsafe_allow_html=True)

with col4:
    st.markdown(f"<div class='metric-box'><h4>⏳ Tool Wear Index</h4><h2>{new_data['Tool_Wear']}%</h2></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ----------------- GRAPHICAL CHARTS (PLOTLY) -----------------
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.write("### 📈 Sensor Telemetry Streams")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['Temperature'], name="Temp (°C)", mode='lines+markers', line=dict(color='#FF4B4B')))
    fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['Vibration'] * 20, name="Vibration (scaled)", mode='lines+markers', line=dict(color='#00F0FF')))
    fig.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=20, b=20), height=350)
    st.plotly_chart(fig, use_container_width=True)

with col_chart2:
    st.write("### 🚨 Predictive Risk Horizon")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df['Timestamp'], y=df['Failure_Prob'], fill='tozeroy', name="Failure Risk %", line=dict(color='#F59E0B')))
    fig2.add_shape(type="line", x0=0, y0=anomaly_threshold, x1=len(df), y1=anomaly_threshold, line=dict(color="Red", dash="dash"))
    fig2.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=20, b=20), height=350, yaxis_range=[0,100])
    st.plotly_chart(fig2, use_container_width=True)

# ----------------- SYSTEM STATUS LOGS & ALERTS -----------------
st.write("### 📋 Smart Maintenance Diagnostics & Action Logs")
if new_data['Failure_Prob'] >= anomaly_threshold:
    st.error(f"🚨 **CRITICAL ALERT:** {machine_id} exceeds safety threshold! Recommended Action: Stop Spindle immediately and schedule Tool Bit replacement.")
elif new_data['Failure_Prob'] >= 40:
    st.warning(f"⚠️ **MAINTENANCE WARNING:** Micro-vibrations and thermal expansion detected. Flagged for review at next shift change.")
else:
    st.success(f"✅ **SYSTEMS OPERATIONAL:** {machine_id} running optimal at {new_data['Spindle_Speed']} RPM.")

# Display historical dataframe
st.dataframe(df.sort_index(ascending=False), use_container_width=True)

# Auto-refresh loop mechanism
time.sleep(sampling_rate)
st.rerun()
