from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://aymandyy.github.io/collab/"}})

# MySQL Connection
db = mysql.connector.connect(
    host="localhost",  
    user="root",       
    password="gurjot",  
    database="student_database"
)

cursor = db.cursor()

# Helper function to check if a student can participate (21-day restriction)
def can_participate(email):
    cursor.execute("SELECT left_date FROM students WHERE email = %s", (email,))
    result = cursor.fetchone()
    if result is None or result[0] is None:
        return True
    left_date = result[0]
    if datetime.utcnow() - left_date >= timedelta(days=21):
        return True
    return False

# Add or Update a Student
@app.route('/add-student', methods=['POST'])
def add_student():
    try:
        data = request.json
        email = data.get("email")
        
        if not can_participate(email):
            return jsonify({"message": "Student is restricted from participating until 21 days have passed."}), 403
        
        # Check if student exists and update or insert
        cursor.execute("SELECT * FROM students WHERE email = %s", (email,))
        existing_student = cursor.fetchone()
        
        if existing_student:
            query = """
            UPDATE students
            SET name = %s, age = %s, mobile_no = %s, qualifications = %s, skill_set = %s,
                school_college_university = %s, department = %s, skill_level = %s, locality = %s
            WHERE email = %s
            """
            cursor.execute(query, (
                data['name'], data['age'], data['mobile_no'], data['qualifications'], data['skill_set'],
                data['school_college_university'], data['department'], data['skill_level'], data['locality'],
                email
            ))
        else:
            query = """
            INSERT INTO students (name, age, mobile_no, email, qualifications, skill_set,
                                  school_college_university, department, skill_level, locality)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                data['name'], data['age'], data['mobile_no'], data['email'], data['qualifications'],
                data['skill_set'], data['school_college_university'], data['department'],
                data['skill_level'], data['locality']
            ))

        db.commit()
        return jsonify({"message": "Student added/updated successfully!"}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"message": "Error adding student", "error": str(e)}), 500

# Mark Student as Leaving the Project
@app.route('/leave-project', methods=['POST'])
def leave_project():
    try:
        email = request.json.get("email")
        if not email:
            return jsonify({"message": "Email is required!"}), 400

        # Update the student's leave date
        cursor.execute("SELECT * FROM students WHERE email = %s", (email,))
        student = cursor.fetchone()
        if student is None:
            return jsonify({"message": "Student not found!"}), 404
        
        cursor.execute("UPDATE students SET left_date = %s WHERE email = %s", (datetime.utcnow(), email))
        db.commit()
        return jsonify({"message": "Student marked as leaving the project!"}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"message": "Error updating student status", "error": str(e)}), 500

# Fetch all students
@app.route('/students', methods=['GET'])
def get_students():
    try:
        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()
        students_list = [{
            "id": student[0], "name": student[1], "age": student[2], "mobile_no": student[3], "email": student[4],
            "qualifications": student[5], "skill_set": student[6], "school_college_university": student[7],
            "department": student[8], "skill_level": student[9], "locality": student[10], "left_date": student[11],
            "created_at": student[12]
        } for student in students]
        return jsonify(students_list), 200
    except Exception as e:
        return jsonify({"message": "Error fetching students", "error": str(e)}), 500

# Fetch a specific student by email
@app.route('/student/<email>', methods=['GET'])
def get_student(email):
    try:
        cursor.execute("SELECT * FROM students WHERE email = %s", (email,))
        student = cursor.fetchone()
        if student is None:
            return jsonify({"message": "Student not found!"}), 404
        student_data = {
            "id": student[0], "name": student[1], "age": student[2], "mobile_no": student[3], "email": student[4],
            "qualifications": student[5], "skill_set": student[6], "school_college_university": student[7],
            "department": student[8], "skill_level": student[9], "locality": student[10], "left_date": student[11],
            "created_at": student[12]
        }
        return jsonify(student_data), 200
    except Exception as e:
        return jsonify({"message": "Error fetching student", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
