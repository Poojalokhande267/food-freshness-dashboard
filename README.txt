SMART FOOD/FRESHNESS BOX — STARTER PACKAGE

IMPORTANT:
- synthetic_demo_dataset.csv is generated synthetic data, not real measurements from fruit.
- train_demo_model.py trains a demonstration model on those synthetic rows.
- A high score on this synthetic dataset does NOT establish real-world freshness/spoilage accuracy.
- Dashboard categories are software-demo outputs only, not food-safety advice.
- The public fruit environment dataset referenced in dashboard.py uses different features (including CO2/light) and is not a direct match for MQ-135/DHT11/DS18B20.

FILES:
1. synthetic_demo_dataset.csv — 12,000 synthetic example rows
2. train_demo_model.py — trains and saves demo_freshness_model.joblib
3. dashboard.py — Streamlit dashboard; manual readings + optional serial read
4. requirements.txt — Python packages

HOW TO RUN ON WINDOWS:
1. Extract this ZIP into your FOODPROJECT folder.
2. Open Command Prompt in that folder.
3. Install packages:
   python -m pip install -r requirements.txt
4. Train the demo model:
   python train_demo_model.py
5. Start the dashboard:
   python -m streamlit run dashboard.py
6. Browser should open the dashboard.

ESP32 SERIAL:
- Use COM7 if that is still your ESP32 port.
- Baud rate must be 115200.
- Close Arduino IDE Serial Monitor before the dashboard tries to read COM7.
- DATA line expected: DATA,gas,dht_temperature,humidity,ds18b20_temperature

NEXT VALIDATION STEP:
To make scientifically meaningful predictions, collect readings from independently assessed samples and label them using a suitable reference method. The synthetic data is only for demonstrating the software pipeline.
