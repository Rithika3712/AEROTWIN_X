import time
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="AeroTwin | Engine Health Dashboard", page_icon="✈️", layout="wide")

st.markdown("""
<style>
    .stApp { background: #071426; color: #e8f1ff; }
    [data-testid="stMetric"] { background: #0d233d; border: 1px solid #1b436a; border-radius: 12px; padding: 12px; }
    h1, h2, h3 { color: #83d4ff; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def generate_data(seed, fault_mode, samples=180):
    rng = np.random.default_rng(seed)
    t = pd.date_range(end=datetime.now(), periods=samples, freq="10s")
    x = np.linspace(0, 1, samples)

    rpm = 2350 + 40 * np.sin(8 * x) + rng.normal(0, 12, samples)
    cht_expected = 176 + 4 * np.sin(7 * x)
    egt_expected = 705 + 9 * np.sin(8 * x)
    oil_p_expected = 58 + 1.5 * np.sin(6 * x)
    vibration_expected = 2.1 + 0.12 * np.sin(10 * x)
    fuel_expected = 35.5 + 0.7 * np.sin(5 * x)

    cht = cht_expected + rng.normal(0, 1.4, samples)
    egt = egt_expected + rng.normal(0, 2.8, samples)
    oil_p = oil_p_expected + rng.normal(0, 0.9, samples)
    vibration = vibration_expected + rng.normal(0, 0.06, samples)
    fuel = fuel_expected + rng.normal(0, 0.3, samples)

    if fault_mode == "Cooling degradation":
        ramp = np.clip((x - 0.55) * 22, 0, None)
        cht += ramp
        egt += ramp * 1.7
    elif fault_mode == "Lubrication degradation":
        ramp = np.clip((x - 0.55) * 16, 0, None)
        oil_p -= ramp
        vibration += ramp * 0.08
    elif fault_mode == "Combustion instability":
        egt += np.clip((x - 0.55) * 28, 0, None) + 8 * np.sin(45 * x)
        vibration += np.clip((x - 0.55) * 0.9, 0, None)
    elif fault_mode == "Sensor drift":
        cht += np.clip((x - 0.35) * 15, 0, None)

    df = pd.DataFrame({
        "time": t,
        "RPM": rpm,
        "CHT Actual": cht,
        "CHT Expected": cht_expected,
        "EGT Actual": egt,
        "EGT Expected": egt_expected,
        "Oil Pressure Actual": oil_p,
        "Oil Pressure Expected": oil_p_expected,
        "Vibration Actual": vibration,
        "Vibration Expected": vibration_expected,
        "Fuel Flow": fuel,
    })
    return df


def trend_chart(df, actual, expected, title, unit, alert_limit=None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["time"], y=df[actual], mode="lines", name="Measured", line=dict(color="#ffb84d", width=3)))
    fig.add_trace(go.Scatter(x=df["time"], y=df[expected], mode="lines", name="Digital Twin Expected", line=dict(color="#35c9ff", dash="dash")))
    if alert_limit is not None:
        fig.add_hline(y=alert_limit, line_dash="dot", line_color="#ff5c5c", annotation_text="Alert threshold")
    fig.update_layout(title=title, height=280, template="plotly_dark", margin=dict(l=10, r=10, t=45, b=10), yaxis_title=unit, legend_orientation="h")
    return fig


st.title("✈️ AeroTwin — Real-Time Engine Health Dashboard")
st.caption("Hybrid Digital Twin + AI anomaly monitoring | Advisory-only prototype")

with st.sidebar:
    st.header("Control Panel")
    engine_id = st.selectbox("Engine ID", ["MALE-ENG-01", "MALE-ENG-02", "TEST-RIG-01"])
    flight_phase = st.selectbox("Flight Phase", ["Cruise", "Climb", "Loiter", "Descent"])
    fault_mode = st.selectbox("Scenario", ["Healthy operation", "Cooling degradation", "Lubrication degradation", "Combustion instability", "Sensor drift"])
    seed = st.slider("Simulation Seed", 1, 100, 21)
    telemetry_on = st.toggle("Live Telemetry", value=True)
    st.divider()
    st.markdown("**Pipeline**")
    st.caption("Sensors → Validation → Digital Twin → AI Analysis → Advisory")

if not telemetry_on:
    st.warning("TELEMETRY LOSS: Data is stale. Dashboard confidence is reduced; no new health conclusion is issued.")

df = generate_data(seed, fault_mode)
latest = df.iloc[-1]

residual_cht = abs(latest["CHT Actual"] - latest["CHT Expected"])
residual_egt = abs(latest["EGT Actual"] - latest["EGT Expected"])
residual_oil = abs(latest["Oil Pressure Actual"] - latest["Oil Pressure Expected"])
residual_vib = abs(latest["Vibration Actual"] - latest["Vibration Expected"])
risk = min(100, int(8 + residual_cht * 2.2 + residual_egt * 0.7 + residual_oil * 4 + residual_vib * 30))
confidence = 96 if telemetry_on else 55

if risk < 30:
    status, status_color, advisory = "NORMAL", "🟢", "Continue routine monitoring."
elif risk < 60:
    status, status_color, advisory = "WARNING", "🟠", "Review trend data and schedule inspection if deviation persists."
else:
    status, status_color, advisory = "HIGH RISK", "🔴", "Inspect affected subsystem before the next mission."

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Engine ID", engine_id)
c2.metric("Flight Phase", flight_phase)
c3.metric("Health Status", f"{status_color} {status}")
c4.metric("Explainable Risk", f"{risk}/100")
c5.metric("Data Confidence", f"{confidence}%")

st.divider()
left, right = st.columns([1.15, 1])

with left:
    st.subheader("Digital Twin Comparison")
    st.plotly_chart(trend_chart(df, "CHT Actual", "CHT Expected", "Cylinder Head Temperature", "°C", 205), use_container_width=True)
    st.plotly_chart(trend_chart(df, "Oil Pressure Actual", "Oil Pressure Expected", "Oil Pressure", "psi", 45), use_container_width=True)

with right:
    st.subheader("AI Health Assessment")
    st.plotly_chart(trend_chart(df, "EGT Actual", "EGT Expected", "Exhaust Gas Temperature", "°C", 760), use_container_width=True)
    st.plotly_chart(trend_chart(df, "Vibration Actual", "Vibration Expected", "Vibration Trend", "g RMS", 3.2), use_container_width=True)

st.divider()
a, b = st.columns([1, 1.4])
with a:
    st.subheader("Explainable Risk Alert")
    risk_label = "Low" if risk < 30 else "Medium" if risk < 60 else "High"
    st.markdown(f"### {status_color} {risk_label} Risk — {risk}/100")
    st.write(f"**Primary evidence:** CHT deviation: {residual_cht:.1f} °C, EGT deviation: {residual_egt:.1f} °C, Oil-pressure deviation: {residual_oil:.1f} psi, Vibration deviation: {residual_vib:.2f} g.")
    st.info(f"**Maintenance advisory:** {advisory}")
    st.caption("Alerts are advisory only. Existing engine protections remain independent.")

with b:
    st.subheader("Data Quality & Mission Replay")
    quality = pd.DataFrame({
        "Check": ["Timestamp synchronization", "Sensor range validation", "Telemetry freshness", "Model validity", "Audit logging"],
        "Status": ["Pass", "Pass", "Live" if telemetry_on else "Stale", "Validated range", "Enabled"],
    })
    st.dataframe(quality, use_container_width=True, hide_index=True)
    st.download_button(
        "Download Mission Telemetry (CSV)",
        df.to_csv(index=False).encode("utf-8"),
        file_name=f"{engine_id}_mission_replay.csv",
        mime="text/csv",
    )

st.caption("Prototype dashboard: simulated/replayed data demonstration. Validate against approved engine and test-rig evidence before operational use.")