import serial
import sqlite3
import time

# 🔌 Change this to your port
PORT = '/dev/ttyACM0'        # e.g., COM4 (Windows) or /dev/ttyUSB0 (Linux)
BAUD = 9600

# Connect to Arduino
ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)  # wait for Arduino to reset

# Create / connect database
conn = sqlite3.connect('solar_data.db')
cursor = conn.cursor()

# Create table
cursor.execute('''
CREATE TABLE IF NOT EXISTS solar_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    ldr_left INTEGER,
    ldr_right INTEGER,
    temperature REAL,
    voltage REAL
)
''')
conn.commit()

print("✅ Connected. Logging data... (Ctrl+C to stop)")

try:
    while True:
        line = ser.readline().decode(errors='ignore').strip()

        if not line:
            continue

        # Ignore non-data lines (like "SWEEP START")
        if ',' not in line:
            print("INFO:", line)
            continue

        parts = line.split(',')

        if len(parts) != 4:
            print("SKIP (bad format):", line)
            continue

        try:
            left = int(parts[0])
            right = int(parts[1])
            temp = float(parts[2])
            volt = float(parts[3])
        except ValueError:
            print("SKIP (parse error):", line)
            continue

        cursor.execute('''
            INSERT INTO solar_data (timestamp, ldr_left, ldr_right, temperature, voltage)
            VALUES (?, ?, ?, ?, ?)
        ''', (time.strftime('%Y-%m-%d %H:%M:%S'), left, right, temp, volt))

        conn.commit()

        print(f"Saved → L:{left} R:{right} Temp:{temp:.2f}C Volt:{volt:.2f}V")

except KeyboardInterrupt:
    print("\n🛑 Stopped by user")

finally:
    ser.close()
    conn.close()
    print("🔌 Closed serial and database")
