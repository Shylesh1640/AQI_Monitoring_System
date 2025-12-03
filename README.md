# 🇮🇳 India AQI Monitoring Dashboard

A real-time, interactive **Air Quality Index (AQI)** dashboard for India built using **Streamlit, Plotly, GeoPandas**, and the **WAQI API**.  
This dashboard provides live AQI updates for major Indian cities, aggregates AQI state-wise, and displays an interactive heatmap with accurate Indian boundaries and a thick national border outline.

---

## ✨ Features

### ✅ Real-Time AQI Fetching
Fetches AQI data from the **WAQI API** for major Indian cities every 15 minutes.

### ✅ State-Level AQI Aggregation
Calculates average AQI per state for accurate visualization.

### ✅ Interactive Plotly Map
- Dynamic color scale based on AQI severity  
- State boundaries outlined clearly  
- Thick India border using dissolved GeoPandas polygon  
- Smooth zoom and pan

### ✅ Auto-Refresh (Every 15 Minutes)
Keeps the data fresh without manually reloading the page.

### ✅ Light/Dark Theme Support
Switches themes automatically based on system settings.

### ✅ Streamlit Metrics Dashboard
Displays:
- National average AQI  
- Most polluted city  
- Cleanest city  
- Total cities monitored  

