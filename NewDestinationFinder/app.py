# app.py
import sqlite3
from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for
import os
import bcrypt
from flask_cors import CORS
import insert_data  # Assuming insert_data.py is in the same directory

app = Flask(__name__)
CORS(app)
DATABASE = r'D:/NewDestinationFinder/data/destination_finder.db'

def get_db_connection():
    try:
        print(f"Attempting connection to: {DATABASE}")
        conn = sqlite3.connect(DATABASE)
        print("Database connection successful!")
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

@app.route('/destinations', methods=['GET'])
def get_destinations():
    try:
        min_temp_str = request.args.get('min_temp')
        max_temp_str = request.args.get('max_temp')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        min_precipitation_str = request.args.get('min_precipitation')
        max_precipitation_str = request.args.get('max_precipitation')
        min_humidity_str = request.args.get('min_humidity')
        max_humidity_str = request.args.get('max_humidity')
        min_wind_speed_str = request.args.get('min_wind_speed')
        max_wind_speed_str = request.args.get('max_wind_speed')
        condition = request.args.get('condition')

        try:
            min_temp = int(min_temp_str) if min_temp_str is not None else None
            max_temp = int(max_temp_str) if max_temp_str is not None else None
        except ValueError:
            return jsonify({"error": "Invalid temperature values. 'min_temp' and 'max_temp' must be integers."}), 400

        try:
            min_precipitation = float(min_precipitation_str) if min_precipitation_str is not None else None
            max_precipitation = float(max_precipitation_str) if max_precipitation_str is not None else None
            min_humidity = float(min_humidity_str) if min_humidity_str is not None else None
            max_humidity = float(max_humidity_str) if max_humidity_str is not None else None
            min_wind_speed = float(min_wind_speed_str) if min_wind_speed_str is not None else None
            max_wind_speed = float(max_wind_speed_str) if max_wind_speed_str is not None else None
        except ValueError:
            return jsonify({"error": "Invalid precipitation, humidity, or wind speed values. Must be numbers."}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        try:
            cur = conn.cursor()
            query = """
                SELECT l.name, l.description, l.image_url,
                    AVG(wd.temperature_high), AVG(wd.temperature_low),
                    AVG(wd.precipitation), AVG(wd.humidity), AVG(wd.wind_speed),
                    wd.condition
                FROM locations l
                JOIN weather_data wd ON l.id = wd.location_id
            """
            params = []
            where_clauses = []

            if start_date and end_date:
                where_clauses.append("STRFTIME('%Y-%m-%d', wd.date) BETWEEN ? AND ?")
                params.extend([start_date, end_date])

            if min_temp is not None and max_temp is not None:
                where_clauses.append("wd.temperature_high BETWEEN ? AND ?")
                params.extend([min_temp, max_temp])

            if min_precipitation is not None and max_precipitation is not None:
                where_clauses.append("wd.precipitation BETWEEN ? AND ?")
                params.extend([min_precipitation, max_precipitation])

            if min_humidity is not None and max_humidity is not None:
                where_clauses.append("wd.humidity BETWEEN ? AND ?")
                params.extend([min_humidity, max_humidity])

            if min_wind_speed is not None and max_wind_speed is not None:
                where_clauses.append("wd.wind_speed BETWEEN ? AND ?")
                params.extend([min_wind_speed, max_wind_speed])

            if condition:
                where_clauses.append("wd.condition LIKE ?")
                params.append(condition)

            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

            query += " GROUP BY l.id"

            cur.execute(query, tuple(params))
            destinations_tuples = cur.fetchall()
            cur.close()
            conn.close()

            destinations = []
            for d in destinations_tuples:
                destinations.append({
                    "name": d[0],
                    "description": d[1],
                    "image_url": "/images/" + d[2],
                    "temperature_high": d[3],
                    "temperature_low": d[4],
                    "precipitation": d[5],
                    "humidity": d[6],
                    "wind_speed": d[7],
                    "condition": d[8]
                })

            return jsonify(destinations)

        except sqlite3.Error as e:
            return jsonify({"error": "Database query failed: " + str(e)}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/images/<filename>')
def get_image(filename):
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)

@app.route('/display_weather_data')
def display_weather_data():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT locations.name, locations.image_url, weather_data.condition, weather_data.temperature_high, weather_data.temperature_low, weather_data.precipitation, weather_data.humidity, weather_data.wind_speed, locations.description FROM weather_data JOIN locations ON weather_data.location_id = locations.id")
        data = cursor.fetchall()
        conn.close()
        return render_template('weather_data.html', data=data)
    else:
        return "Error connecting to database."

@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        try:
            cur = conn.cursor()
            cur.execute("SELECT password FROM users WHERE email = ?", (email,))
            result = cur.fetchone()

            if result:
                stored_password = result[0].decode('utf-8')
                if bcrypt.checkpw(password, stored_password):
                    return redirect(url_for('weather_data'))
                else:
                    return render_template('login.html', error="Incorrect password")
            else:
                return render_template('login.html', error="User not found")
        except sqlite3.Error as e:
            return jsonify({'error': f'Database query failed: {e}'}), 500
        finally:
            if conn:
                conn.close()

    return render_template('login.html')

@app.route('/weather_data', methods=['GET', 'POST'])
def weather_data():
    conn = get_db_connection()
    if not conn:
        return "Database connection failed"

    weather_data = []
    if request.method == 'POST':
        condition = request.form.get('condition')

        try:
            cur = conn.cursor()
            query = """
                SELECT l.name, l.image_url, wd.condition, wd.temperature_high, wd.temperature_low, wd.precipitation, wd.humidity, wd.wind_speed, l.description
                FROM weather_data wd
                JOIN locations l ON wd.location_id = l.id
                WHERE 1=1
            """
            params = []

            if condition:
                query += " AND wd.condition LIKE ?"
                params.append(f"%{condition}%")

            cur.execute(query, params)
            weather_data = cur.fetchall()
        except sqlite3.Error as e:
            return f"Database query failed: {e}"
        finally:
            if conn:
                conn.close()
    else:
        try:
            cur = conn.cursor()
            query = """
                SELECT l.name, l.image_url, wd.condition, wd.temperature_high, wd.temperature_low, wd.precipitation, wd.humidity, wd.wind_speed, l.description
                FROM weather_data wd
                JOIN locations l ON wd.location_id = l.id
            """
            cur.execute(query)
            weather_data = cur.fetchall()
        except sqlite3.Error as e:
            return f"Database query failed: {e}"
        finally:
            if conn:
                conn.close()

    return render_template('weather_data.html', weather_data=weather_data)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        condition = request.form['season']

        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        conn = get_db_connection()
        if not conn:
            print("Failed to get database connection in signup function")
            return jsonify({"error": "Database connection failed"}), 500

        try:
            cur = conn.cursor()
            query = "INSERT INTO users (fullname, email, password, season) VALUES (?, ?, ?, ?)"
            params = (fullname, email, hashed_password, condition)

            cur.execute(query, params)
            conn.commit()

            insert_data.insert_data(condition)

            query = """
                SELECT l.name, l.image_url, wd.condition, wd.temperature_high, wd.temperature_low, wd.precipitation, wd.humidity, wd.wind_speed, l.description
                FROM weather_data wd
                JOIN locations l ON wd.location_id = l.id
                WHERE wd.condition LIKE ?
            """
            params = (f"%{condition}%",)

            cur.execute(query, params)
            weather_data = cur.fetchall()

            return render_template('weather_data.html', weather_data=weather_data)

        except sqlite3.IntegrityError:
            conn.rollback()
            return jsonify({"error": "Email already exists"}), 409

        except sqlite3.Error as e:
            conn.rollback()
            print(f'Database query failed: {e}')
            return jsonify({'error': f'Database query failed: {e}'}), 500

        finally:
            if 'cur' in locals():
                cur.close()
            if 'conn' in locals():
                conn.close()

    return render_template('signup.html')

if __name__ == '__main__':
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("DROP TABLE IF EXISTS weather_data")
            cur.execute("DROP TABLE IF EXISTS locations")
            cur.execute("DROP TABLE IF EXISTS users")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS locations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    description TEXT,
                    image_url TEXT
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS weather_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    location_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    temperature_high REAL,
                    temperature_low REAL,
                    precipitation REAL,
                    humidity REAL,
                    wind_speed REAL,
                    cloud_cover REAL,
                    condition TEXT,
                    FOREIGN KEY (location_id) REFERENCES locations(id),
                    UNIQUE (location_id, date, condition)
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fullname TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    season TEXT
                )
            """)
            conn.commit()
            cur.close()
            conn.close()
            print("Tables created (or already existed).")

        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")

    app.run(debug=True, port=5003)
