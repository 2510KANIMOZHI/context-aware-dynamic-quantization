from flask import Flask, render_template, request, jsonify
import sqlite3
import random
from datetime import datetime

app = Flask(__name__)

# ---------------- DATABASE ----------------

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quantization_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device TEXT,
            model_size REAL,
            quantization_level TEXT,
            energy_saved REAL,
            latency REAL,
            timestamp TEXT
        )
    ''')

    conn.commit()
    conn.close()

# ---------------- HOME PAGE ----------------

@app.route('/')
def home():
    return render_template('index.html')

# ---------------- OPTIMIZATION ----------------

@app.route('/optimize', methods=['POST'])
def optimize():

    data = request.get_json()

    device = data['device']
    model_size = float(data['model_size'])

    if model_size > 500:
        quantization = 'INT4'
        energy_saved = round(random.uniform(70, 85), 2)
        latency = round(random.uniform(10, 20), 2)

    elif model_size > 200:
        quantization = 'INT8'
        energy_saved = round(random.uniform(45, 65), 2)
        latency = round(random.uniform(20, 35), 2)

    else:
        quantization = 'FP16'
        energy_saved = round(random.uniform(20, 40), 2)
        latency = round(random.uniform(35, 50), 2)

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO quantization_logs
        (device, model_size, quantization_level, energy_saved, latency, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        device,
        model_size,
        quantization,
        energy_saved,
        latency,
        timestamp
    ))

    conn.commit()
    conn.close()

    return jsonify({
        'device': device,
        'quantization': quantization,
        'energy_saved': energy_saved,
        'latency': latency,
        'timestamp': timestamp
    })

# ---------------- HISTORY ----------------

@app.route('/history')
def history():

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM quantization_logs ORDER BY id DESC')

    rows = cursor.fetchall()

    conn.close()

    logs = []

    for row in rows:
        logs.append({
            'device': row[1],
            'model_size': row[2],
            'quantization': row[3],
            'energy_saved': row[4],
            'latency': row[5],
            'timestamp': row[6]
        })

    return jsonify(logs)

# ---------------- MAIN ----------------

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
