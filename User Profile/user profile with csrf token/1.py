import secrets
from flask import Flask, request, jsonify
import random
import smtplib
from email.mime.text import MIMEText
from flask_wtf.csrf import generate_csrf
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///about.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_hex(16)  # Secret key for Flask session
app.config['JWT_SECRET_KEY'] = 'dc6f8cf55952d4550b2a54a1a79b6398'  # Secret key for JWT
jwt = JWTManager(app)
db = SQLAlchemy(app)

csrf = CSRFProtect(app)

class User(db.Model):
    username = db.Column(db.String(80), primary_key=True)
    password = db.Column(db.String(80))
    email = db.Column(db.String(120))
    date_of_birth = db.Column(db.String(10))
    gender = db.Column(db.String(10))
    otp = db.Column(db.Integer)


def send_otp_email(receiver_email, otp):
    # Replace with your email server details
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'etemp7354@gmail.com'
    smtp_password = 'fomx muls ofkf egdk'

    sender_email = 'etemp7354@gmail.com'

    subject = 'Your OTP for User Profile Management'
    body = f'Your OTP is: {otp}'

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, [receiver_email], msg.as_string())


@app.route('/signup', methods=['POST'])
@csrf.exempt
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    date_of_birth = data.get('date_of_birth')
    gender = data.get('gender')

    if username and password and email and date_of_birth and gender:
        existing_user = db.session.query(User).get(username)
        if existing_user:
            return jsonify({"error": "Username already exists"}), 400

        new_user = User(username=username, password=password, email=email, date_of_birth=date_of_birth, gender=gender,
                        otp=None)
        db.session.add(new_user)
        db.session.commit()

        csrf_token = generate_csrf()

        # Include CSRF token in the response
        response = jsonify({"message": "Signup successful"})
        response.headers["X-CSRF-TOKEN"] = csrf_token
        return response, 200

    else:
        return jsonify({"error": "Username, password, email, date_of_birth, and gender are required"}), 400


@app.route('/login', methods=['POST'])
@csrf.exempt
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    existing_user = User.query.filter_by(username=username, password=password).first()

    if existing_user:
        # Successful login, generate and send OTP
        otp = random.randint(1000, 9999)
        existing_user.otp = otp
        db.session.commit()

        # Send OTP via email
        send_otp_email(existing_user.email, otp)

        return jsonify({"message": "Login successful. OTP generated and sent via email"}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401


@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@app.route('/verify_otp', methods=['POST'])
@csrf.exempt
def verify_otp():
    data = request.json
    username = data.get('username')
    otp_attempt = data.get('otp')

    existing_user = User.query.filter_by(username=username, otp=otp_attempt).first()

    if existing_user:
        existing_user.otp = None  # Reset OTP after successful verification
        db.session.commit()
        return jsonify({"message": "OTP verification successful"}), 200
    else:
        return jsonify({"error": "Invalid OTP"}), 401


@app.route('/get_profile/<username>', methods=['GET'])
@csrf.exempt
def get_profile(username):
    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        user_profile = {
            'username': existing_user.username,
            'password': existing_user.password,
            'email': existing_user.email,
            'date_of_birth': existing_user.date_of_birth,
            'gender': existing_user.gender
        }
        return jsonify(user_profile), 200
    else:
        return jsonify({"error": "User not found"}), 404


@app.route('/update_profile/<username>', methods=['PUT'])
@csrf.exempt
def update_profile(username):
    data = request.json

    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        existing_user.password = data.get('password', existing_user.password)
        existing_user.email = data.get('email', existing_user.email)
        existing_user.date_of_birth = data.get('date_of_birth', existing_user.date_of_birth)
        existing_user.gender = data.get('gender', existing_user.gender)

        db.session.commit()

        return jsonify({"message": "Profile updated successfully"}), 200
    else:
        return jsonify({"error": "User not found"}), 404


@app.route('/forgot_password', methods=['POST'])
@csrf.exempt
def forgot_password():
    data = request.json
    username = data.get('username')

    user = User.query.get(username)

    if user:
        # In a real-world scenario, you would implement a password reset mechanism, potentially sending a reset link
        return jsonify({"message": "Password reset instructions sent"}), 200
    else:
        return jsonify({"error": "User not found"}), 4044


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)