from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import pyotp  # To generate OTP

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://aymandyy.github.io/collab/"}}))

# Temporary storage for users and OTPs (in-memory for simplicity)
users = {}
otps = {}

# Generate OTP function
def generate_otp(mobile_no):
    otp = random.randint(100000, 999999)  # Generate a random 6-digit OTP
    otps[mobile_no] = otp  # Store the OTP for verification later
    return otp

# Endpoint for user login (mobile number)
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        mobile_no = data.get("mobile_no")
        
        if not mobile_no:
            return jsonify({"message": "Mobile number is required!"}), 400
        
        # Simulating user lookup, assuming the user exists
        if mobile_no not in users:
            users[mobile_no] = {"mobile_no": mobile_no}  # Add new user if not exist
        
        # Generate OTP for the given mobile number
        otp = generate_otp(mobile_no)
        
        # Simulate sending OTP (you would use a service like Twilio here)
        print(f"Sending OTP: {otp} to mobile number {mobile_no}")
        
        return jsonify({"message": "OTP sent successfully!", "otp": otp}), 200  # Send OTP in the response for testing
    
    except Exception as e:
        return jsonify({"message": "Error during login", "error": str(e)}), 500

# Endpoint for OTP verification
@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    try:
        data = request.json
        mobile_no = data.get("mobile_no")
        otp = data.get("otp")
        
        if not mobile_no or not otp:
            return jsonify({"message": "Mobile number and OTP are required!"}), 400
        
        # Check if OTP matches
        if otps.get(mobile_no) == otp:
            return jsonify({"message": "OTP verified successfully!"}), 200
        else:
            return jsonify({"message": "Invalid OTP!"}), 400
    
    except Exception as e:
        return jsonify({"message": "Error during OTP verification", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
