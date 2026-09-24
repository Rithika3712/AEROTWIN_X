# AeroTwin — AI-Enabled Real-Time Digital Twin for MALE UAV Engine Health Monitoring

A hybrid **Digital Twin + Explainable AI** dashboard for real-time health monitoring, fault detection, and predictive maintenance advisory for MALE UAV piston engines (Rotax-914 class).

---

## ✈️ Overview

AeroTwin implements a **residual-based anomaly detection** architecture where a physics-informed digital twin generates expected sensor values, and deviations (residuals) are scored into an explainable risk index. The system provides actionable maintenance advisories while remaining **advisory-only** (non-binding to engine protections).

**Key Features:**
- Real-time telemetry simulation with fault injection
- Digital twin expected-value modeling
- Residual-based anomaly detection
- Explainable risk scoring (0–100)
- Interactive Streamlit dashboard with Plotly visualizations
- Mission replay and CSV export

---

## 🏗️ System Architecture

Sensors --> Validation --> Digital Twin --> AI Analysis --> Advisory


### Pipeline Stages

1. **Data Acquisition & Validation** — Simulated telemetry with noise and fault signatures
2. **Digital Twin Expected-Value Model** — Thermodynamic baseline for CHT, EGT, Oil Pressure, Vibration
3. **Residual Computation** — Absolute deviation between measured and expected
4. **Explainable Risk Scoring** — Weighted sum of residuals → 0–100 risk index
5. **Maintenance Advisory** — Three-tier classification (NORMAL / WARNING / HIGH RISK)

---

## 🔬 Technical Approach

### 1. Digital Twin Expected-Value Model

The digital twin computes expected sensor values based on simplified thermodynamic relationships:

| Sensor | Baseline | Variation Model |
|--------|----------|-----------------|
| CHT (°C) | 176 | Sinusoidal load variation ±4°C |
| EGT (°C) | 705 | Combustion dynamics ±9°C |
| Oil Pressure (psi) | 58 | Pump ripple ±1.5 psi |
| Vibration (g RMS) | 2.1 | Mechanical resonance ±0.12 g |

In production, these would be conditioned on flight phase, altitude, and ambient conditions.

### 2. Fault Injection Mechanisms

Four degradation modes emulate common failure signatures:

| Fault Mode | Signature |
|------------|-----------|
| **Cooling degradation** | Monotonic CHT & EGT rise after mid-mission |
| **Lubrication degradation** | Oil pressure drop + vibration increase |
| **Combustion instability** | EGT spikes + high-frequency vibration |
| **Sensor drift** | Gradual CHT bias without physical cause |

### 3. Residual-Based Anomaly Detection

For each sensor:

\[
r_{\text{sensor}} = | \text{Actual} - \text{Expected} |
\]

Residuals are interpretable, low-latency, and robust to limited labeled fault data.

### 4. Explainable Risk Scoring

Composite risk index:

\[
\text{Risk} = \min\left(100,\; 8 + 2.2\,r_{\text{CHT}} + 0.7\,r_{\text{EGT}} + 4\,r_{\text{Oil}} + 30\,r_{\text{Vib}}\right)
\]

**Coefficient rationale:**
- Vibration (30×): High sensitivity to mechanical faults
- Oil pressure (4×): Critical for lubrication health
- CHT (2.2×): Thermal stress indicator
- EGT (0.7×): Combustion efficiency proxy

### 5. Risk Classification

| Risk Range | Status | Advisory |
|------------|--------|----------|
| 0–29 | 🟢 NORMAL | Continue routine monitoring |
| 30–59 | 🟠 WARNING | Review trends; schedule inspection |
| 60–100 | 🔴 HIGH RISK | Inspect subsystem before next mission |

---

## 📦 Installation

### Prerequisites

- Python 3.10+
- pip

### Install Dependencies

```bash
pip install streamlit pandas numpy plotly
```

---

## 🚀 Usage

### 1. Run the Dashboard

```bash
cd C:\Users\STUDENT\OneDrive\Desktop\aerotwin_x
python -m streamlit run dashboard.py
```

### 2. Open in Browser

Navigate to:

http://localhost:8501


### 3. Interact with Controls

- **Engine ID**: Select engine instance
- **Flight Phase**: Cruise, Climb, Loiter, Descent
- **Scenario**: Healthy or fault mode
- **Simulation Seed**: Reproducible telemetry
- **Live Telemetry**: Toggle real-time vs. stale data

### 4. Export Mission Data

Click **Download Mission Telemetry (CSV)** to save the simulated time-series.

---

## 📊 Dashboard Components

### Left Panel — Digital Twin Comparison
- CHT Actual vs. Expected (°C)
- Oil Pressure Actual vs. Expected (psi)

### Right Panel — AI Health Assessment
- EGT Actual vs. Expected (°C)
- Vibration Actual vs. Expected (g RMS)

### Bottom Panel — Explainable Risk Alert
- Risk score (0–100)
- Primary evidence (residuals per sensor)
- Maintenance advisory

### Data Quality Panel
- Timestamp synchronization
- Sensor range validation
- Telemetry freshness (Live/Stale)
- Model validity
- Audit logging

---

## 🧪 Simulation Details

### Data Generation

- **Samples**: 180 time steps (30 minutes at 10-second intervals)
- **Noise**: Gaussian sensor noise (σ varies by sensor)
- **Fault Ramps**: Linear degradation after 55% mission time

### Telemetry Signals

| Signal | Unit | Baseline | Noise σ |
|--------|------|----------|---------|
| RPM | rev/min | 2350 | 12 |
| CHT | °C | 176 | 1.4 |
| EGT | °C | 705 | 2.8 |
| Oil Pressure | psi | 58 | 0.9 |
| Vibration | g RMS | 2.1 | 0.06 |
| Fuel Flow | L/h | 35.5 | 0.3 |

---

## 🔐 Safety & Compliance Notes

- **Advisory-only**: Alerts do not override engine protections (e.g., FADEC limits)
- **Prototype**: Validate against approved engine and test-rig evidence before operational use
- **Audit Trail**: Future versions will log all alerts and residuals for compliance

---

## 🛣️ Future Enhancements (Production Roadmap)

1. **Real Telemetry Integration** — CAN/FADEC stream ingestion
2. **Adaptive Digital Twin** — Condition expected values on flight phase, altitude, temperature
3. **ML-Based Anomaly Detection** — LSTM or Isolation Forest for pattern-based fault classification
4. **Remaining Useful Life (RUL)** — Survival models (e.g., Cox PH) for prognostics
5. **Uncertainty Quantification** — Confidence intervals on risk scores
6. **Multi-Engine Fleet Monitoring** — Parallel engine instances with comparative analytics
7. **Cloud Deployment** — Scalable architecture for fleet-wide monitoring

---

## 📚 References & Alignment

This implementation aligns with:

- **Residual-based fault detection** using analytical redundancy
- **Hybrid digital twins** combining physics models with data-driven corrections
- **Explainable predictive maintenance** with transparent risk scoring
- **Real-time Streamlit dashboards** for interactive monitoring

---

## 📄 License

Prototype for research and demonstration. Validate against approved evidence before operational deployment.

---

## 👨‍💻 Author

AeroTwin Development Team — AI-Enabled Real-Time Digital Twin System for MALE UAV Engine Health Monitoring