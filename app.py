from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
import io
import joblib
import pandas as pd
import requests
import datetime
import random
import math
import threading
import webbrowser
import urllib.parse
import time
import pyautogui
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import psycopg2
import os
from werkzeug.utils import secure_filename

NEON_DB_URL = "postgresql://neondb_owner:npg_mhMBTQlu3sb7@ep-proud-breeze-anyi86ow-pooler.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

app = Flask(__name__)
app.secret_key = "super_secure_admin_key_for_samsung_project" # Required for logins

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Make sure the folder exists when the app starts
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- 1. Load All Trained AI Models ---
# Make sure these .pkl files are in the same folder as app.py
fire_model = joblib.load('forest_fire_predictor_model.pkl')
landslide_model = joblib.load('landslide_predictor_model.pkl')
flood_model = joblib.load('flood_predictor_model.pkl')
cyclone_model = joblib.load('cyclone_predictor_model.pkl')
earthquake_model = joblib.load('earthquake_predictor_model.pkl')
print("All AI models loaded successfully!")
# --- Live Demo Variables ---
demo_tick = 0
live_history = {'time': [], 'Temperature': [], 'Humidity': [], 'Wind': []}
live_logs = []
sos_already_sent = False  # Lock flag to avoid repeated tab spawning during one disaster window.

# Put the exact phone numbers you want to alert here (must include country code like +91)
target_numbers = ["+919894810613","+919080427681","+919047056070","+917708682468","+919344911279"]


def send_whatsapp_sos(msg):
    """Run WhatsApp sending in the background using native browser tools and PyAutoGUI."""
    print(f"Starting automated SOS broadcast to {len(target_numbers)} contacts...")

    for number in target_numbers:
        try:
            print(f"Opening WhatsApp Web for {number}...")

            # Format the message safely into a URL
            encoded_msg = urllib.parse.quote(msg)
            whatsapp_url = f"https://web.whatsapp.com/send?phone={number}&text={encoded_msg}"

            # Open the chat in a new tab
            webbrowser.open(whatsapp_url)

            # 1. WAIT LONGER: Give WhatsApp Web 20 seconds to completely load the UI
            time.sleep(20)

            # 2. PRESS ENTER TWICE: First to focus the box (if needed), second to send!
            pyautogui.press('enter')
            time.sleep(1)
            pyautogui.press('enter')

            print(f"SOS sent automatically to {number}!")

            # 3. WAIT BEFORE CLOSING: Give the message 5 seconds to leave your outbox
            time.sleep(5)

            # Close the current tab
            pyautogui.hotkey('ctrl', 'w')

            # Wait 2 seconds before looping to the next number
            time.sleep(2)

        except Exception as e:
            print(f"Failed to automate sending to {number}: {e}")

    print("SOS Broadcast Complete!")


def _predict_with_feature_alignment(model, values_by_name, aliases=None):
    """Predict using model feature names when available to avoid column-order mismatches."""
    aliases = aliases or {}

    if hasattr(model, "feature_names_in_"):
        feature_row = {}
        for feature in model.feature_names_in_:
            keys_to_try = [feature] + aliases.get(feature, [])
            value = None
            for key in keys_to_try:
                if key in values_by_name:
                    value = values_by_name[key]
                    break

            # Auto-handle one-hot soil columns from a single Soil_Type dropdown.
            if value is None and feature.startswith("Soil_Type_"):
                soil_name = feature.replace("Soil_Type_", "")
                value = 1.0 if values_by_name.get("Soil_Type") == soil_name else 0.0

            if value is None:
                raise ValueError(f"Missing required input for model feature: {feature}")

            feature_row[feature] = float(value)

        X = pd.DataFrame([feature_row], columns=model.feature_names_in_)
        return model.predict(X)[0]

    # Fallback for models saved without feature name metadata.
    ordered_values = [float(v) for v in values_by_name.values()]
    return model.predict([ordered_values])[0]

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # --- NEON DB PLACEHOLDER ---
        # Later, we will replace this if statement with a PostgreSQL query!
        if username == 'admin' and password == 'admin123':
            session['is_admin'] = True
            return redirect(url_for('home'))
        else:
            error = "Invalid Credentials. Access Denied."

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('is_admin', None) # Erases the admin cookie
    return redirect(url_for('home'))

# --- 2. Page Navigation Routes ---
@app.route('/')
def home():
    posts = []
    try:
        # Fetch the latest news from Neon DB to show on the homepage
        with psycopg2.connect(NEON_DB_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, title, content, image_filename, likes_count, post_time FROM news_posts ORDER BY post_time DESC LIMIT 10;")
                rows = cur.fetchall()
                for row in rows:
                    posts.append({
                        'id': row[0], 'title': row[1], 'content': row[2],
                        'image': row[3], 'likes': row[4],
                        'time': row[5].strftime("%b %d, %Y - %I:%M %p")
                    })
    except Exception as e:
        print(f"Database Error: {e}")

    return render_template('index.html', posts=posts)

@app.route('/wildfire')
def wildfire_page(): return render_template('wildfire.html')

@app.route('/landslide')
def landslide_page(): return render_template('landslide.html')

@app.route('/flood')
def flood_page(): return render_template('flood.html')

@app.route('/cyclone')
def cyclone_page(): return render_template('cyclone.html')

@app.route('/earthquake')
def earthquake_page(): return render_template('earthquake.html')

@app.route('/all-in-one')
def all_in_one_page(): return render_template('all_in_one.html')

@app.route('/live_dashboard')
@app.route('/live-dashboard')
def live_dashboard_page(): 
    # SECURITY CHECK: If they are not logged in as admin, redirect them to the home page!
    if not session.get('is_admin'):
        return redirect(url_for('home'))

    return render_template('live_dashboard.html')

@app.route('/update_logic')
def update_logic():
    global demo_tick, sos_already_sent
    demo_tick += 1
    now = datetime.datetime.now().strftime('%H:%M:%S')

    # 1. Generate Realistic Sensor Data
    base_temp = 24.0 + (math.sin(demo_tick * 0.5) * 1.5) + random.uniform(-0.5, 0.5)
    base_rh, base_ws, base_rain = 65.0, 12.0, 0.5

    # Trigger disaster every 8th tick
    if demo_tick % 8 == 0:
        temp, rh, ws, rain = 42.0, 12.0, 38.0, 0.0
    else:
        temp, rh, ws, rain = base_temp, base_rh, base_ws, base_rain

    temp, rh, ws, rain = round(temp, 1), round(rh, 1), round(ws, 1), round(rain, 1)

    # 2. Ask the AI
    prediction = fire_model.predict([[temp, rh, ws, rain]])
    is_disaster = bool(prediction[0] == 1)

    # ==========================================
    # 3. SAVE TO NEON CLOUD DATABASE
    # ==========================================
    try:
        # We use a context manager (with) so the connection closes automatically
        with psycopg2.connect(NEON_DB_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO live_sensor_logs
                    (log_time, temperature, humidity, wind, rain, is_disaster)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (now, temp, rh, ws, rain, is_disaster))
            conn.commit() # Save the changes to the database
    except Exception as e:
        print(f"Database Error: {e}")
    # ==========================================

    # 4. WhatsApp SOS logic
    if is_disaster and not sos_already_sent:
        sos_already_sent = True

        alert_msg = (
            f"URGENT SOS\n"
            f"Disaster Management System triggered!\n"
            f"Temp: {temp} C, Wind: {ws} km/h.\n"
            f"Evacuate immediately."
        )

        threading.Thread(target=send_whatsapp_sos, args=(alert_msg,), daemon=True).start()

    elif not is_disaster:
        sos_already_sent = False

    # 5. Save to history
    live_history['time'].append(now)
    live_history['Temperature'].append(temp)
    live_history['Humidity'].append(rh)
    live_history['Wind'].append(ws)

    if len(live_history['time']) > 15:
        for key in live_history:
            live_history[key].pop(0)

    # 6. Generate logs
    if is_disaster:
        log_text = f"<span style='color: #fb7185;'>[{now}] 🔴 SOS TRIGGERED! Temp: {temp}°C - WhatsApp Alert Initiated!</span>"
    else:
        log_text = f"[{now}] 🟢 Normal | Temp: {temp}°C | RH: {rh}%"

    live_logs.insert(0, log_text)
    if len(live_logs) > 15:
        live_logs.pop()

    return jsonify({"logs": live_logs, "disaster": is_disaster})


@app.route('/get_graph/<parameter>')
def get_graph(parameter):
    # This route physically draws the graph in Python and sends it as an image.
    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor('#1a2634')
    ax.set_facecolor('#1a2634')

    if len(live_history['time']) > 0 and parameter in live_history:
        color = '#ffaa00' if parameter == 'Temperature' else '#38bdf8'
        ax.plot(live_history['time'], live_history[parameter], color=color, marker='o', linewidth=2)

    # Make the graph text white
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('white')

    plt.title(f"Live {parameter} Tracking", color='white', fontsize=14)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the plot to memory and send it to HTML
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close(fig)

    return send_file(img, mimetype='image/png')

# --- 3. Prediction Action Routes ---

@app.route('/predict_wildfire', methods=['POST'])
def predict_wildfire():
    # 1. Grab inputs
    temp = float(request.form['Temperature'])
    rh = float(request.form['RH'])
    ws = float(request.form['Ws'])
    rain = float(request.form['Rain'])

    # 2. Get AI Prediction
    prediction = fire_model.predict([[temp, rh, ws, rain]])
    is_disaster = bool(prediction[0] == 1)

    # 3. Generate the "Why" and the "Theme" (Ideas 3 & 4)
    reasons = []

    if is_disaster:
        theme = "danger-glow"
        result_text = "🔴 HIGH RISK: Fire conditions detected!"
        # Analyze the data to find the culprits
        if temp >= 35:
            reasons.append(f"Temperature ({temp}°C) is critically high, drying out fuels rapidly.")
        if rh <= 30:
            reasons.append(f"Relative Humidity ({rh}%) is dangerously low.")
        if ws >= 20:
            reasons.append(f"Wind Speed ({ws}km/h) is strong enough to spread embers.")
        if rain == 0:
            reasons.append("Zero rainfall creates a highly flammable environment.")
        # Fallback just in case
        if not reasons:
            reasons.append("The combined weather conditions match historical wildfire disaster patterns.")
    else:
        theme = "safe-glow"
        result_text = "🟢 Safe: Low fire risk."
        reasons.append("Environmental conditions are currently stable.")
        if rain > 2:
            reasons.append(f"Recent rainfall ({rain}mm) is keeping the environment moist.")
        if temp < 25:
            reasons.append(f"Cooler temperatures ({temp}°C) are mitigating fire risks.")

    # 4. Send everything to HTML
    return render_template('wildfire.html', result=result_text, theme=theme, reasons=reasons)

@app.route('/predict_landslide', methods=['POST'])
def predict_landslide():
    rain = float(request.form['Rainfall_mm'])
    slope = float(request.form['Slope_Angle'])
    soil_str = request.form['Soil_Type']

    # FIX: Convert the text into a single number instead of 3 separate variables
    if soil_str == "Gravel":
        soil_num = 0
    elif soil_str == "Sand":
        soil_num = 1
    else: # Silt
        soil_num = 2

    # Now we are feeding exactly 3 features! (Rain, Slope, Soil_Num)
    prediction = landslide_model.predict([[rain, slope, soil_num]])
    is_disaster = bool(prediction[0] == 1)

    reasons = []
    if is_disaster:
        theme = "danger-glow"
        result_text = "🔴 WARNING: High Landslide Probability!"
        if rain > 100:
            reasons.append(f"Heavy rainfall ({rain}mm) is heavily loosening the terrain.")
        if slope > 30:
            reasons.append(f"The steep slope angle ({slope}°) is highly prone to gravity-driven collapse.")
        reasons.append(f"The identified soil type ({soil_str}) has low structural cohesion when wet.")
        if not reasons:
            reasons.append("Geological and weather patterns indicate slope failure is imminent.")
    else:
        theme = "safe-glow"
        result_text = "🟢 Safe: Low landslide risk."
        reasons.append("Terrain stability is currently uncompromised.")
        if slope < 20:
            reasons.append(f"The gentle slope ({slope}°) significantly reduces gravitational risks.")
        if soil_str == "Gravel":
            reasons.append("Gravel terrain provides good drainage and structural stability.")

    return render_template('landslide.html', result=result_text, theme=theme, reasons=reasons)

@app.route('/predict_flood', methods=['POST'])
def predict_flood():
    rain = float(request.form['Rainfall_mm'])
    river = float(request.form['River_Level_m'])
    hum = float(request.form['Humidity_pct'])
    temp = float(request.form['Temperature_C'])
    soil = float(request.form['Soil_Moisture_pct'])
    wind = float(request.form['Wind_Speed_kmph'])

    prediction = flood_model.predict([[rain, river, hum, temp, soil, wind]])
    is_disaster = bool(prediction[0] == 1)

    reasons = []
    if is_disaster:
        theme = "danger-glow"
        result_text = "🔴 WARNING: Flood Imminent!"
        if rain > 80:
            reasons.append(f"Heavy rainfall ({rain}mm) is overwhelming local drainage.")
        if river > 5:
            reasons.append(f"River levels are dangerously high at {river}m.")
        if soil > 65:
            reasons.append(f"Soil moisture is saturated ({soil}%), meaning the ground cannot absorb more water.")
        if not reasons:
            reasons.append("The combination of these hydrological factors signals a severe flood event.")
    else:
        theme = "safe-glow"
        result_text = "🟢 Safe: No flood risk."
        reasons.append("Hydrological levels are within normal, safe limits.")
        if river < 3:
            reasons.append(f"River levels ({river}m) are well below flood stage.")
        if soil < 50:
            reasons.append("The soil has sufficient capacity to absorb expected rainfall.")

    return render_template('flood.html', result=result_text, theme=theme, reasons=reasons)

@app.route('/predict_cyclone', methods=['POST'])
def predict_cyclone():
    lat = float(request.form['latitude'])
    lon = float(request.form['longitude'])
    sst = float(request.form['sea_surface_temp_C'])
    hum = float(request.form['humidity_percent'])
    pressure = float(request.form['pressure_hPa'])
    wind = float(request.form['wind_speed_kmph'])

    prediction = cyclone_model.predict([[lat, lon, sst, hum, pressure, wind]])
    result_label = str(prediction[0])

    reasons = []
    if result_label.lower() in ["high", "medium"]:
        theme = "danger-glow"
        result_text = f"🔴 Cyclone Risk Level: {result_label.upper()}"
        if sst >= 26.5:
            reasons.append(f"Warm sea surface temperature ({sst}°C) is providing massive energy for cyclone formation.")
        if pressure <= 1000:
            reasons.append(f"Low atmospheric pressure ({pressure}hPa) indicates a strong storm center.")
        if wind > 60:
            reasons.append(f"High baseline wind speeds ({wind}km/h) suggest dangerous cyclonic circulation.")
        if not reasons:
            reasons.append("Oceanic and atmospheric conditions are aligning perfectly for a cyclonic event.")
    else:
        theme = "safe-glow"
        result_text = f"🟢 Safe: Cyclone Risk {result_label.upper()}"
        reasons.append("Atmospheric pressure and sea surface temperatures are currently stable.")
        if pressure > 1010:
            reasons.append(f"Normal atmospheric pressure ({pressure}hPa) prevents cyclone formation.")
        if sst < 26:
            reasons.append(f"Cooler sea temperatures ({sst}°C) lack the energy needed to feed a tropical storm.")

    return render_template('cyclone.html', result=result_text, theme=theme, reasons=reasons)

@app.route('/predict_earthquake', methods=['POST'])
def predict_earthquake():
    lat = float(request.form['latitude'])
    lon = float(request.form['longitude'])
    depth = float(request.form['depth_km'])
    mag = float(request.form['magnitude'])
    fault = float(request.form['fault_distance_km'])
    freq = float(request.form['seismic_frequency'])
    tremors = float(request.form['micro_tremors'])
    plate = float(request.form['plate_movement'])

    prediction = earthquake_model.predict([[lat, lon, depth, mag, fault, freq, tremors, plate]])
    result_label = str(prediction[0])

    reasons = []
    if result_label.lower() in ["high", "medium"]:
        theme = "danger-glow"
        result_text = f"🔴 Earthquake Risk Level: {result_label.upper()}"
        if fault < 50:
            reasons.append(f"Proximity to the fault line ({fault}km) drastically increases danger.")
        if tremors > 15:
            reasons.append(f"A high cluster of micro tremors ({tremors}) suggests building tectonic stress.")
        if plate > 20:
            reasons.append(f"Rapid plate movement ({plate}mm/yr) creates extreme subterranean friction.")
        if not reasons:
            reasons.append("Seismic anomalies strongly indicate an impending major earthquake.")
    else:
        theme = "safe-glow"
        result_text = f"🟢 Safe: Earthquake Risk {result_label.upper()}"
        reasons.append("Tectonic plates in this region are currently showing minimal abnormal friction.")
        if fault > 100:
            reasons.append(f"The distance from major fault lines ({fault}km) safely lowers the risk.")
        if tremors < 5:
            reasons.append(f"Micro-tremor activity ({tremors}) is at a very normal baseline.")

    return render_template('earthquake.html', result=result_text, theme=theme, reasons=reasons)


@app.route('/predict_all', methods=['POST'])
def predict_all():
    city = request.form['city']

    try:
        # 1. Fetch latitude/longitude from city name
        geo_resp = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "format": "json"},
            timeout=15,
        )
        geo_resp.raise_for_status()
        geo_data = geo_resp.json()

        if 'results' not in geo_data or not geo_data['results']:
            return "City not found. Please go back and try again."

        lat = float(geo_data['results'][0]['latitude'])
        lon = float(geo_data['results'][0]['longitude'])
        city_name = geo_data['results'][0]['name']

        # 2. Fetch current weather conditions
        weather_resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,rain,wind_speed_10m,surface_pressure",
            },
            timeout=15,
        )
        weather_resp.raise_for_status()
        weather_data = weather_resp.json()['current']

        temp = float(weather_data.get('temperature_2m', 0.0))
        rh = float(weather_data.get('relative_humidity_2m', 0.0))
        rain = float(weather_data.get('rain', 0.0))
        wind = float(weather_data.get('wind_speed_10m', 0.0))
        pressure = float(weather_data.get('surface_pressure', 1010.0))

        # 3. Wildfire
        fire_values = {
            'Temperature': temp,
            'Temp': temp,
            'RH': rh,
            'Ws': wind,
            'Rain': rain,
        }
        fire_pred = _predict_with_feature_alignment(
            fire_model,
            fire_values,
            aliases={'Temp': ['Temperature'], 'Temperature': ['Temp']},
        )
        fire_res = "HIGH RISK" if fire_pred == 1 else "Safe"

        # 4. Flood (live + fallback mock values where needed)
        flood_values = {
            'Rainfall_mm': rain,
            'River_Level_m': 3.0,
            'Humidity_pct': rh,
            'Temperature_C': temp,
            'Soil_Moisture_pct': 50.0,
            'Wind_Speed_kmph': wind,
        }
        flood_pred = _predict_with_feature_alignment(flood_model, flood_values)
        flood_res = "WARNING: Flood Imminent" if flood_pred == 1 else "Safe"

        # 5. Cyclone
        cyclone_values = {
            'latitude': lat,
            'longitude': lon,
            'sea_surface_temp_C': 28.0,
            'humidity_percent': rh,
            'pressure_hPa': pressure,
            'wind_speed_kmph': wind,
        }
        cyclone_pred = _predict_with_feature_alignment(cyclone_model, cyclone_values)
        cyclone_res = f"Risk Level: {cyclone_pred}"

        # 6. Earthquake (location + mocked seismic indicators)
        earthquake_values = {
            'latitude': lat,
            'longitude': lon,
            'depth_km': 40.0,
            'magnitude': 3.0,
            'fault_distance_km': 100.0,
            'seismic_frequency': 10.0,
            'micro_tremors': 0.0,
            'plate_movement': 15.0,
            'plate_movement_mm_per_year': 15.0,
        }
        eq_pred = _predict_with_feature_alignment(
            earthquake_model,
            earthquake_values,
            aliases={'plate_movement_mm_per_year': ['plate_movement']},
        )
        eq_res = f"Risk Level: {eq_pred}"

        # 7. Landslide (live rain + mocked topography/soil fallback values)
        landslide_values = {
            'Rainfall_mm': rain,
            'Slope_Angle': 25.0,
            'Soil_Type': 'Silt',
            'Soil_Type_Gravel': 0.0,
            'Soil_Type_Sand': 0.0,
            'Soil_Type_Silt': 1.0,
            'Soil_Saturation': max(0.0, min(1.0, rain / 300.0)),
            'Vegetation_Cover': 0.5,
            'Proximity_to_Water': 0.5,
        }
        land_pred = _predict_with_feature_alignment(landslide_model, landslide_values)
        land_res = "WARNING: Landslide Probability" if land_pred == 1 else "Safe"

        # 8. Render dashboard
        return render_template(
            'all_results.html',
            city=city_name,
            lat=lat,
            lon=lon,
            temp=temp,
            rain=rain,
            wind=wind,
            fire_res=fire_res,
            flood_res=flood_res,
            cyclone_res=cyclone_res,
            earthquake_res=eq_res,
            landslide_res=land_res,
        )

    except Exception as e:
        return f"API Error: {str(e)}"


# ==========================================
# NEWS & UPDATES SYSTEM (NEON DB)
# ==========================================

@app.route('/news')
def news_feed():
    """Public page to view all official updates."""
    posts = []
    try:
        with psycopg2.connect(NEON_DB_URL) as conn:
            with conn.cursor() as cur:
                # Fetch all posts, newest first!
                cur.execute("SELECT id, title, content, image_filename, likes_count, post_time FROM news_posts ORDER BY post_time DESC;")
                rows = cur.fetchall()
                # Convert the raw database rows into a nice dictionary for HTML
                for row in rows:
                    posts.append({
                        'id': row[0], 'title': row[1], 'content': row[2],
                        'image': row[3], 'likes': row[4],
                        'time': row[5].strftime("%b %d, %Y - %I:%M %p")
                    })
    except Exception as e:
        print(f"Database Error: {e}")

    return render_template('news_feed.html', posts=posts)

@app.route('/admin/create_post', methods=['GET', 'POST'])
def create_post():
    """Admin page to publish a new update."""
    # Security Check: Kick out normal users!
    if not session.get('is_admin'):
        return redirect(url_for('home'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        image_file = request.files.get('image')
        filename = None

        # Save the uploaded image if the admin attached one
        if image_file and image_file.filename != '':
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Insert into Neon DB
        try:
            with psycopg2.connect(NEON_DB_URL) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO news_posts (title, content, image_filename)
                        VALUES (%s, %s, %s)
                    """, (title, content, filename))
                conn.commit()
            return redirect(url_for('news_feed'))
        except Exception as e:
            print(f"Database Error: {e}")
            return "Failed to post update."

    return render_template('create_post.html')

@app.route('/news/like/<int:post_id>', methods=['POST'])
def like_post(post_id):
    """Adds +1 to the like counter for a specific post."""
    try:
        with psycopg2.connect(NEON_DB_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE news_posts SET likes_count = likes_count + 1 WHERE id = %s", (post_id,))
            conn.commit()
    except Exception as e:
        print(f"Database Error: {e}")

    # Send a success signal back to the browser
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)