from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Database setup
DB_NAME = "students.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                mobile_no TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                qualifications TEXT NOT NULL,
                skill_set TEXT NOT NULL,
                institution TEXT NOT NULL,
                department TEXT NOT NULL,
                skill_level TEXT NOT NULL CHECK(skill_level IN ('newbee', 'intermediate', 'professional')),
                left_date TEXT DEFAULT NULL
            )
        """)
        conn.commit()

# Helper function to check the 21-day restriction
def can_participate(email):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT left_date FROM students WHERE email = ?", (email,))
        row = cursor.fetchone()
        if not row or not row[0]:
            return True
        left_date = datetime.strptime(row[0], "%Y-%m-%d")
        return datetime.utcnow() - left_date >= timedelta(days=21)

# Add or update student
@app.route('/add-student', methods=['POST'])
def add_student():
    try:
        data = request.json
        email = data.get("email")

        if not can_participate(email):
            return jsonify({"message": "Student is restricted from participating until 21 days have passed."}), 403

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO students (name, age, mobile_no, email, qualifications, skill_set, institution, department, skill_level, left_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
                ON CONFLICT(email) DO UPDATE SET
                    name = excluded.name,
                    age = excluded.age,
                    mobile_no = excluded.mobile_no,
                    qualifications = excluded.qualifications,
                    skill_set = excluded.skill_set,
                    institution = excluded.institution,
                    department = excluded.department,
                    skill_level = excluded.skill_level,
                    left_date = NULL
            """, (
                data["name"],
                data["age"],
                data["mobile_no"],
                data["email"],
                data["qualifications"],
                data["skill_set"],
                data["institution"],
                data["department"],
                data["skill_level"]
            ))
            conn.commit()

        return jsonify({"message": "Student added/updated successfully!"}), 201
    except Exception as e:
        return jsonify({"message": "Error adding student", "error": str(e)}), 500

# Mark a student as leaving the project
@app.route('/leave-project', methods=['POST'])
def leave_project():
    try:
        email = request.json.get("email")
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE students SET left_date = ? WHERE email = ?", (datetime.utcnow().strftime("%Y-%m-%d"), email))
            if cursor.rowcount == 0:
                return jsonify({"message": "Student not found!"}), 404
            conn.commit()
        return jsonify({"message": "Student marked as leaving the project!"}), 200
    except Exception as e:
        return jsonify({"message": "Error updating student status", "error": str(e)}), 500

# Fetch all students
@app.route('/students', methods=['GET'])
def get_students():
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students")
            students = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            result = [dict(zip(columns, row)) for row in students]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"message": "Error fetching students", "error": str(e)}), 500

# Fetch a specific student by email
@app.route('/student/<email>', methods=['GET'])
def get_student(email):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE email = ?", (email,))
            row = cursor.fetchone()
            if not row:
                return jsonify({"message": "Student not found!"}), 404
            columns = [column[0] for column in cursor.description]
            student = dict(zip(columns, row))
        return jsonify(student), 200
    except Exception as e:
        return jsonify({"message": "Error fetching student", "error": str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
