from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://aymandyy.github.io/collab/"}})

# MySQL Connection
db = mysql.connector.connect(
    host="localhost",  
    user="root",       
    password="your_password",  
    database="mentor_database"
)

cursor = db.cursor()

# Helper function to check team assignment constraint
def can_assign_team(email):
    cursor.execute("SELECT current_team_count FROM mentors WHERE email = %s", (email,))
    result = cursor.fetchone()
    if result and result[0] < 2:
        return True
    return False

# Add or Update a Mentor
@app.route('/add-mentor', methods=['POST'])
def add_mentor():
    try:
        data = request.json
        email = data.get("email")
        
        # Check if mentor exists
        cursor.execute("SELECT * FROM mentors WHERE email = %s", (email,))
        existing_mentor = cursor.fetchone()
        
        if existing_mentor:
            query = """
            UPDATE mentors
            SET name = %s, experience = %s, mobile_no = %s, qualifications = %s, 
                skill_set = %s, past_achievements = %s, locality = %s
            WHERE email = %s
            """
            cursor.execute(query, (
                data['name'], data['experience'], data['mobile_no'], data['qualifications'],
                data['skill_set'], data['past_achievements'], data['locality'], email
            ))
        else:
            query = """
            INSERT INTO mentors (name, experience, mobile_no, email, qualifications, 
                                 skill_set, past_achievements, locality)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                data['name'], data['experience'], data['mobile_no'], data['email'],
                data['qualifications'], data['skill_set'], data['past_achievements'], data['locality']
            ))

        db.commit()
        return jsonify({"message": "Mentor added/updated successfully!"}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"message": "Error adding/updating mentor", "error": str(e)}), 500

# Assign a Team to a Mentor
@app.route('/assign-team', methods=['POST'])
def assign_team():
    try:
        email = request.json.get("email")
        if not email:
            return jsonify({"message": "Email is required!"}), 400

        if not can_assign_team(email):
            return jsonify({"message": "Mentor cannot guide more than two teams at a time."}), 403
        
        # Increment the mentor's current_team_count
        cursor.execute("UPDATE mentors SET current_team_count = current_team_count + 1 WHERE email = %s", (email,))
        db.commit()
        return jsonify({"message": "Team assigned successfully!"}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"message": "Error assigning team", "error": str(e)}), 500

# Fetch all mentors
@app.route('/mentors', methods=['GET'])
def get_mentors():
    try:
        cursor.execute("SELECT * FROM mentors")
        mentors = cursor.fetchall()
        mentors_list = [{
            "id": mentor[0], "name": mentor[1], "experience": mentor[2], "mobile_no": mentor[3], 
            "email": mentor[4], "qualifications": mentor[5], "skill_set": mentor[6], 
            "past_achievements": mentor[7], "locality": mentor[8], "current_team_count": mentor[9],
            "created_at": mentor[10]
        } for mentor in mentors]
        return jsonify(mentors_list), 200
    except Exception as e:
        return jsonify({"message": "Error fetching mentors", "error": str(e)}), 500

# Fetch a specific mentor by email
@app.route('/mentor/<email>', methods=['GET'])
def get_mentor(email):
    try:
        cursor.execute("SELECT * FROM mentors WHERE email = %s", (email,))
        mentor = cursor.fetchone()
        if mentor is None:
            return jsonify({"message": "Mentor not found!"}), 404
        mentor_data = {
            "id": mentor[0], "name": mentor[1], "experience": mentor[2], "mobile_no": mentor[3],
            "email": mentor[4], "qualifications": mentor[5], "skill_set": mentor[6],
            "past_achievements": mentor[7], "locality": mentor[8], "current_team_count": mentor[9],
            "created_at": mentor[10]
        }
        return jsonify(mentor_data), 200
    except Exception as e:
        return jsonify({"message": "Error fetching mentor", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
