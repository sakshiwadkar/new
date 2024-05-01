from flask import Flask, request, jsonify, session
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_session import Session  # Import Flask-Session
from models import db, User
import random
import requests

app = Flask(__name__)

app.config['SECRET_KEY'] = 'cairocoders-ednalan'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost/bookdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)
db.init_app(app)

# Configure and Initialize Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

with app.app_context():
    db.create_all()

@app.route("/")
def hello_world():
    return "Hello, World!"

@app.route("/send-otp", methods=["POST"])
def send_otp():
    email = request.json["email"]
    otp = random.randint(1000, 9999)
    session['otp'] = otp
    session['email'] = email
    
    app.logger.info("Session Data After Setting OTP: %s", session)
    
    # Construct email body with OTP
    email_body = f"<html><body><h2>Your OTP is:</h2><p>{otp}</p></body></html>"
    
    # Send email using Elastic Email API
    response = requests.post(
        "https://api.elasticemail.com/v2/email/send",
        data={
            "apikey": "696B1C556C0611EF31D8A02E22987AAD361EE51547B47CFC8A56DDBBB4F00CA215F783AEB4C1C9AE5B9256ECF422F2F4",  # Replace with your Elastic Email API key
            "subject": "Email OTP",
            "from": "its94364@gmail.com",  # Replace with your sender email
            "to": email,
            "bodyHtml": email_body
        }
    )
    
    if response.status_code == 200:
        return jsonify({"message": "OTP sent successfully", "otp": otp})
    else:
        return jsonify({"error": "Failed to send OTP"}), 500

@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    try:
        data = request.json
        email = data.get("email")
        entered_otp = data.get("otp")

        if not email or not entered_otp:
            return jsonify({"error": "Email and OTP are required."}), 400

        stored_otp = session.get('otp')
        if stored_otp is None:
            return jsonify({"error": "OTP not found in session"}), 400

        if str(entered_otp) == str(stored_otp):
            return jsonify({"message": "OTP verified successfully"})
        else:
            return jsonify({"error": "Invalid OTP"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/register", methods=["POST"])
def signup():
    email = request.json["email"]
    password = request.json["password"]
    role = request.json["role"]  # New

    user_exists = User.query.filter_by(email=email).first() is not None

    if user_exists:
        return jsonify({"error": "Email already exists"}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email=email, password=hashed_password, role=role)  # Updated
    db.session.add(new_user)

    try:
        db.session.commit()
        session["user_id"] = new_user.id
        return jsonify({
            "id": new_user.id,
            "email": new_user.email,
            "role": new_user.role  # Return role in response
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/login", methods=["POST"])
def login_user():
    email = request.json["email"]
    password = request.json["password"]

    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"error": "Unauthorized Access"}), 401

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Unauthorized"}), 401

    session["user_id"] = user.id
    session["user_role"] = user.role  # New

    return jsonify({
        "id": user.id,
        "email": user.email,
        "role": user.role  # Return role in response
    })

@app.route("/reset_password", methods=["POST"])
def reset_password():
    email = request.json["email"]
    new_password = request.json["new_password"]

    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"error": "User not found"}), 404

    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    user.password = hashed_password

    try:
        db.session.commit()
        return jsonify({"message": "Password reset successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
