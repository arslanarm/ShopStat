import sqlite3

from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from classes.class_db_connector import DBConnector
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename

conn = sqlite3.connect('stat_database.db', check_same_thread=False)

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@cross_origin()
@app.route('/get_rows', methods=['GET'])
def get_rows():
    # Get request parameters
    start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d %H:%M:%S')
    end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d %H:%M:%S')
    print(start_date, end_date)
    # Query the database
    cur = conn.cursor()
    cur.execute("SELECT * FROM videos WHERE date BETWEEN ? AND ?", (start_date, end_date))
    rows = cur.fetchall()

    # Format the response as JSON
    result = []
    for row in rows:
        result.append({
            'in': row[0],
            'out': row[1],
            'id': row[2],
            'date': row[3]
        })

    return jsonify(result)


@cross_origin()
@app.route('/get_rows_this_week', methods=['GET'])
def get_rows_this_week():
    # Calculate start and end of current week
    now = datetime.now()
    week_start = now - timedelta(days=now.weekday())
    week_end = week_start + timedelta(days=6)
    # Query the database
    cur = conn.cursor()
    cur.execute("SELECT * FROM videos WHERE date BETWEEN ? AND ?", (week_start, week_end))
    rows = cur.fetchall()
    # Format the response as JSON
    result = []
    for row in rows:
        print(row)
        result.append({
            'id': row[0],
            'out': row[1],
            'in': row[2],
            'date': row[3]
        })

    return jsonify(result)


@cross_origin()
@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')

    try:
        # Insert user into database
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()

        return jsonify({'message': 'User registered successfully!'})

    except sqlite3.IntegrityError:
        # Duplicate username error
        return jsonify({'error': 'Username already exists!'}), 400


# Login endpoint
@cross_origin()
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    # Query database for user
    cursor = conn.execute("SELECT id, username, password FROM users WHERE username = ? AND password = ?",
                          (username, password))
    user = cursor.fetchone()

    if user:
        return jsonify({'message': 'Login successful!'})

    else:
        return jsonify({'error': 'Invalid username or password!'}), 401


@cross_origin()
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    filename = secure_filename(file.filename)
    file.save(f'videos/{filename}')
    return {'message': f'File {filename} has been uploaded'}


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
