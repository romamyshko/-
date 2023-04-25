import sqlite3
from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)
tokens = {}

@app.route('/students', methods=['GET'])
def get_students():
    conn = sqlite3.connect('db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students')
    students = cursor.fetchall()
    conn.close()
    return jsonify(students)

@app.route('/token/<string:nickname>', methods=['GET'])
def get_token(nickname):
    conn = sqlite3.connect('db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students WHERE nickname=?', (nickname,))
    student = cursor.fetchone()
    conn.close()
    if student:
        token = uuid.uuid4().hex
        tokens[nickname] = token
        return jsonify(token=token)
    else:
        return jsonify(error='Student not found'), 404

@app.route('/students', methods=['POST'])
def create_student():
    if 'Token' not in request.headers:
        return jsonify(error='Token is missing'), 403
    received_token = request.headers['Token']
    if received_token not in tokens.values():
        return jsonify(error='Invalid token'), 403
    data = request.get_json()
    conn = sqlite3.connect('db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO students (nickname, first_name, last_name) VALUES (?, ?, ?)',
                   (data['nickname'], data['first_name'], data['last_name']))
    conn.commit()
    conn.close()
    return jsonify(message='Student created'), 201

if __name__ == '__main__':
    app.run(debug=True)
