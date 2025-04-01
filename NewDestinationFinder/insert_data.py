import sqlite3

def insert_data(condition):
    conn = None
    try:
        conn = sqlite3.connect('D:/NewDestinationFinder/data/destination_finder.db')
        cursor = conn.cursor()

        # Check if locations table is empty
        cursor.execute("SELECT COUNT(*) FROM locations")
        if cursor.fetchone()[0] == 0:
            locations = [
                ('Goa', 15.2995, 74.1240, 'Beautiful beaches', 'goa.jpg'),
                ('Shimla', 31.1048, 77.1734, 'Hill station', 'shimla.jpg'),
                ('Kerala', 8.9003, 76.5812, 'Tropical paradise', 'kerala.jpg'),
                ('Jaipur', 26.9220, 75.8267, 'Pink City', 'jaipur.jpg'),
                ('Udaipur', 24.5854, 73.7125, 'City of Lakes', 'udaipur.jpg'),
                ('Manali', 32.2432, 77.1896, 'Mountain Resort', 'manali.jpg'),
                ('Meghalaya', 25.4670, 91.3662, 'Land of Clouds', 'meghalaya.jpg'),
                ('London', 51.5074, -0.1278, 'Historic city', 'london.jpg'),
                ('Tokyo', 35.6895, 139.6917, 'Modern metropolis', 'tokyo.jpg'),
                ('New York', 40.7128, -74.0060, 'Urban center', 'newyork.jpg'),
                ('Paris', 48.8566, 2.3522, 'Romantic city', 'paris.jpg'),
                ('Sydney', -33.8688, 151.2093, 'Coastal city', 'sydney.jpg'),
                ('Rio de Janeiro', -22.9068, -43.1729, 'Vibrant beaches', 'rio.jpg'),
                ('Cairo', 30.0444, 31.2357, 'Ancient pyramids', 'cairo.jpg'),
                ('Moscow', 55.7558, 37.6173, 'Historical capital', 'moscow.jpg'),
                ('Dubai', 25.2048, 55.2708, 'Luxury city', 'dubai.jpg'),
                ('Cape Town', -33.9249, 18.4241, 'Scenic landscapes', 'capetown.jpg'),
                ('Buenos Aires', -34.6037, -58.3816, 'Cultural city', 'buenosaires.jpg'),
                ('Toronto', 43.6532, -79.3832, 'Multicultural hub', 'toronto.jpg'),
                ('Berlin', 52.5200, 13.4050, 'Historical landmarks', 'berlin.jpg'),
                ('Rome', 41.9028, 12.4964, 'Ancient ruins', 'rome.jpg'),
                ('Bangkok', 13.7563, 100.5018, 'Tropical city', 'bangkok.jpg'),
                ('Auckland', -36.8485, 174.7633, 'Harbor city', 'auckland.jpg'),
                ('Vancouver', 49.2827, -123.1207, 'Coastal mountains', 'vancouver.jpg'),
                ('Helsinki', 60.1699, 24.9384, 'Seaside capital', 'helsinki.jpg')
            ]

            for location in locations:
                cursor.execute("INSERT OR IGNORE INTO locations (name, latitude, longitude, description, image_url) VALUES (?, ?, ?, ?, ?)", location)
            conn.commit()
            print("Locations data inserted.")
        else:
            print("Locations table already populated.")

        cursor.execute("SELECT id, name FROM locations")
        location_ids = {name: id for id, name in cursor.fetchall()}

        if condition == 'Sunny':
            weather_data = [
                ('Goa', '2024-07-01', 32, 25, 0.0, 70, 15, 20, 'Sunny'),
                ('Sydney', '2024-07-01', 28, 20, 0.0, 65, 12, 10, 'Sunny'),
                ('Dubai', '2024-07-01', 42, 32, 0.0, 30, 25, 5, 'Sunny'),
                ('Rio de Janeiro', '2024-07-01', 30, 24, 0.0, 75, 18, 15, 'Sunny'),
            ]
        elif condition == 'Arid':
            weather_data = [
                ('Jaipur', '2024-07-01', 40, 30, 0.0, 20, 20, 5, 'Arid'),
                ('Cairo', '2024-07-01', 38, 28, 0.0, 25, 15, 3, 'Arid')
            ]
        elif condition == 'Cloudy':
            weather_data = [
                ('Shimla', '2024-07-01', 22, 15, 10.0, 80, 8, 80, 'Cloudy'),
                ('London', '2024-07-01', 18, 12, 15.0, 85, 10, 90, 'Cloudy'),
                ('Berlin', '2024-07-01', 20, 14, 12.0, 82, 9, 85, 'Cloudy')
            ]
        elif condition == 'Partly Cloudy':
            weather_data = [
                ('Kerala', '2024-07-01', 28, 22, 2.0, 75, 10, 30, 'Partly Cloudy'),
                ('New York', '2024-07-01', 25, 18, 5.0, 70, 15, 40, 'Partly Cloudy'),
                ('Toronto', '2024-07-01', 24, 17, 4.0, 68, 14, 35, 'Partly Cloudy')
            ]
        elif condition == 'Mostly Sunny':
            weather_data = [
                ('Udaipur', '2024-07-01', 33, 26, 1.0, 65, 10, 20, 'Mostly Sunny'),
                ('Paris', '2024-07-01', 27, 20, 2.0, 60, 11, 25, 'Mostly Sunny'),
                ('Rome', '2024-07-01', 29, 22, 3.0, 62, 12, 28, 'Mostly Sunny')
            ]
        elif condition == 'Snowy':
            weather_data = [
                ('Manali', '2024-07-01', 18, 10, 15.0, 90, 5, 95, 'Snowy'),
                ('Moscow', '2024-07-01', -5, -10, 20.0, 95, 3, 100, 'Snowy'),
                ('Helsinki', '2024-07-01', -2, -8, 18.0, 92, 4, 98, 'Snowy')
            ]
        elif condition == 'Rainy':
            weather_data = [
                ('Meghalaya', '2024-07-01', 25, 20, 50.0, 95, 12, 100, 'Rainy'),
                ('Tokyo', '2024-07-01', 26, 21, 40.0, 90, 14, 95, 'Rainy'),
                ('Bangkok', '2024-07-01', 30, 25, 35.0, 88, 16, 90, 'Rainy')
            ]
        else:
            weather_data = []

        for data in weather_data:
            location_name, date, temp_high, temp_low, precip, humid, wind, cloud, cond = data
            location_id = location_ids.get(location_name)
            if location_id:
                cursor.execute("SELECT 1 FROM weather_data WHERE location_id = ? AND date = ? AND condition = ?", (location_id, date, cond))
                if cursor.fetchone() is None:
                    cursor.execute("INSERT INTO weather_data (location_id, date, temperature_high, temperature_low, precipitation, humidity, wind_speed, cloud_cover, condition) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                    (location_id, date, temp_high, temp_low, precip, humid, wind, cloud, cond))
                    conn.commit()
                else:
                    print(f"Weather data already exists for '{location_name}' on {date} with condition '{cond}'.")
            else:
                print(f"Location '{location_name}' not found.")

        print(f"Data inserted successfully for {condition}!")

    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"Database error: {e}")

    finally:
        if conn:
            if 'cursor' in locals():
                cursor.close()
            conn.close()
