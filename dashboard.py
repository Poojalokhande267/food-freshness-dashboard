import streamlit as st
import pandas as pd
import joblib
import serial
import time
from datetime import datetime

st.set_page_config(
    page_title="Smart Food Freshness Box",
    page_icon="🍎",
    layout="wide"
)

st.title("🍎 Smart Food/Fruit Freshness Box")

st.warning(
    "DEMONSTRATION MODEL: Trained on synthetic data. "
    "The output cannot confirm whether food is fresh, spoiled, or safe to eat."
)

# Load the trained machine learning model
@st.cache_resource
def load_bundle():
    return joblib.load("demo_freshness_model.joblib")


try:
    bundle = load_bundle()
    model = bundle["model"]
    features = bundle["features"]

except Exception as e:
    st.error(
        "Model file not found or could not be loaded. "
        "Run python train_demo_model.py first."
    )
    st.code(str(e))
    st.stop()


# Initialize session variables
if "monitoring" not in st.session_state:
    st.session_state.monitoring = False

if "latest_reading" not in st.session_state:
    st.session_state.latest_reading = None

if "history" not in st.session_state:
    st.session_state.history = []


# --------------------------------------------------
# LIVE ESP32 MONITORING
# --------------------------------------------------

st.header("📡 Live Sensor Monitoring")

port = st.text_input("ESP32 COM Port", value="COM7")

col1, col2 = st.columns(2)

with col1:
    if st.button("▶ Start Monitoring"):
        st.session_state.monitoring = True

with col2:
    if st.button("⏹ Stop Monitoring"):
        st.session_state.monitoring = False


if st.session_state.monitoring:

    st.info("Live monitoring is active.")

    try:
        # Open the ESP32 serial connection
        with serial.Serial(
            port=port,
            baudrate=115200,
            timeout=2
        ) as esp:

            # Allow the serial connection to initialize
            time.sleep(2)

            found = None
            deadline = time.time() + 8

            # Wait for a valid sensor reading
            while time.time() < deadline:

                line = esp.readline().decode(
                    "utf-8",
                    errors="ignore"
                ).strip()

                if line.startswith("DATA,"):

                    values = line.split(",")

                    if len(values) == 5:

                        try:
                            found = {
                                "Time": datetime.now().strftime(
                                    "%H:%M:%S"
                                ),
                                "MQ135_Raw": float(values[1]),
                                "DHT11_Temperature_C": float(values[2]),
                                "Humidity_Percent": float(values[3]),
                                "DS18B20_Temperature_C": float(values[4])
                            }

                            break

                        except ValueError:
                            continue

        # Save the new reading
        if found is not None:

            st.session_state.latest_reading = found

            st.session_state.history.append(found)

            # Keep the latest 100 readings
            st.session_state.history = (
                st.session_state.history[-100:]
            )

        else:
            st.warning(
                "No valid DATA line received. Check the ESP32, "
                "COM port, baud rate, and sensor code."
            )

    except Exception as e:

        st.error(f"Serial connection error: {e}")


# --------------------------------------------------
# DISPLAY LATEST SENSOR READINGS
# --------------------------------------------------

reading = st.session_state.latest_reading

if reading is not None:

    st.header("🌡️ Latest Sensor Readings")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "MQ-135 Gas Reading",
        f"{reading['MQ135_Raw']:.0f}"
    )

    col2.metric(
        "DHT11 Temperature",
        f"{reading['DHT11_Temperature_C']:.2f} °C"
    )

    col3.metric(
        "Humidity",
        f"{reading['Humidity_Percent']:.2f}%"
    )

    col4.metric(
        "DS18B20 Temperature",
        f"{reading['DS18B20_Temperature_C']:.2f} °C"
    )

    st.caption(f"Last reading received at {reading['Time']}")


    # --------------------------------------------------
    # MACHINE LEARNING PREDICTION
    # --------------------------------------------------

    row = pd.DataFrame([{
        "MQ135_Raw": reading["MQ135_Raw"],
        "DHT11_Temperature_C": reading["DHT11_Temperature_C"],
        "Humidity_Percent": reading["Humidity_Percent"],
        "DS18B20_Temperature_C": reading["DS18B20_Temperature_C"]
    }])[features]

    prediction = model.predict(row)[0]

    probabilities = model.predict_proba(row)[0]

    score = float(max(probabilities))


    # --------------------------------------------------
    # FRESHNESS STATUS
    # --------------------------------------------------

    st.header("🍎 Food Freshness Status")

    if prediction == "Fresh":

        st.success("🟢 FRESH — Demo Classification")

    elif prediction == "Monitor":

        st.warning("🟡 MONITOR — Demo Classification")

    elif prediction == "Possible Spoilage":

        st.error("🔴 POSSIBLE SPOILAGE — Demo Classification")

    else:

        st.info(f"Demo Classification: {prediction}")


    st.metric(
        "Model Score (not verified reliability)",
        f"{score:.1%}"
    )

    st.caption(
        "This status is generated by a model trained on synthetic data. "
        "It is not validated against real fruit-spoilage measurements "
        "and must not be used to determine food safety."
    )


    # --------------------------------------------------
    # SENSOR HISTORY
    # --------------------------------------------------

    if st.session_state.history:

        st.header("📊 Sensor Reading History")

        history_df = pd.DataFrame(
            st.session_state.history
        )

        st.dataframe(
            history_df.tail(10),
            use_container_width=True
        )

        st.subheader("Sensor Trends")

        st.line_chart(
            history_df.set_index("Time")[
                [
                    "MQ135_Raw",
                    "DHT11_Temperature_C",
                    "DS18B20_Temperature_C"
                ]
            ]
        )

else:

    st.info(
        "Connect your ESP32 and click Start Monitoring "
        "to receive sensor readings."
    )


# Automatically refresh during monitoring
if st.session_state.monitoring:

    time.sleep(2)

    st.rerun()


# --------------------------------------------------
# MANUAL SENSOR INPUT
# --------------------------------------------------

st.divider()

st.header("📝 Manual Sensor Prediction")

with st.form("manual_form"):

    gas = st.number_input(
        "MQ-135 Raw Reading",
        min_value=0,
        max_value=4095,
        value=134
    )

    dht_temp = st.number_input(
        "DHT11 Temperature (°C)",
        min_value=0.0,
        max_value=80.0,
        value=30.3
    )

    humidity = st.number_input(
        "Humidity (%)",
        min_value=0.0,
        max_value=100.0,
        value=52.0
    )

    ds_temp = st.number_input(
        "DS18B20 Temperature (°C)",
        min_value=0.0,
        max_value=80.0,
        value=31.56
    )

    predict_button = st.form_submit_button(
        "Predict Demo Category"
    )


if predict_button:

    row = pd.DataFrame([{
        "MQ135_Raw": gas,
        "DHT11_Temperature_C": dht_temp,
        "Humidity_Percent": humidity,
        "DS18B20_Temperature_C": ds_temp
    }])[features]

    prediction = model.predict(row)[0]

    probabilities = model.predict_proba(row)[0]

    score = float(max(probabilities))

    st.subheader("🍎 Manual Prediction Result")

    if prediction == "Fresh":

        st.success("🟢 FRESH — Demo Classification")

    elif prediction == "Monitor":

        st.warning("🟡 MONITOR — Demo Classification")

    elif prediction == "Possible Spoilage":

        st.error("🔴 POSSIBLE SPOILAGE — Demo Classification")

    else:

        st.info(f"Demo Classification: {prediction}")

    st.metric(
        "Model Score (not verified reliability)",
        f"{score:.1%}"
    )

    st.caption(
        "Demonstration only. The model has not been validated "
        "using real food-spoilage data."
    )


# --------------------------------------------------
# PROJECT INFORMATION
# --------------------------------------------------

st.divider()

st.subheader("ℹ️ About This Project")

st.write(
    """
    This prototype combines an ESP32 with an MQ-135 gas sensor,
    a DHT11 temperature and humidity sensor, and a DS18B20
    temperature sensor.

    Sensor readings are displayed in a dashboard and processed
    by a demonstration machine learning model.

    The current model uses synthetic data. Real experimental
    measurements and validation are required before its output
    can be interpreted as an actual food-freshness assessment.
    """
)