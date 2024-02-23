from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pyotp
import base64
import os

app = Flask(__name__)

# Use a global dictionary to store user data
users = {}

def generate_random_secret():
    # Generate a random 20-byte key
    random_key = os.urandom(20)
    # Base32 encode the key
    base32_encoded_key = base64.b32encode(random_key).decode('utf-8')
    return base32_encoded_key

def generate_otp(secret):
    totp = pyotp.TOTP(secret)
    return totp.now()

def send_otp_email(email, otp):
    # Email configuration
    sender_email = 'etemp7354@gmail.com'
    app_password = 'fomx muls ofkf egdk'

    # Message configuration
    subject = 'OTP Verification'
    body = f'Your OTP for email verification: {otp}'

    # Create the MIMEText object
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = subject

    # Attach body to the message
    msg.attach(MIMEText(body, 'plain'))

    # Connect to Gmail SMTP server
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        # Start TLS for security
        server.starttls()

        # Login with your Gmail account
        server.login(sender_email, app_password)

        # Send the email
        server.sendmail(sender_email, email, msg.as_string())

    print("OTP email sent successfully!")

def verify_otp(user_otp, secret):
    totp = pyotp.TOTP(secret)

    print(f"Generated OTP: {totp.now()}")
    print(f"User Entered OTP: {user_otp}")

    return totp.verify(user_otp)

@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()

    if 'email' not in data:
        return jsonify({'error': 'Email is required'}), 400

    email = data['email']

    # Generate a random secret key
    secret = generate_random_secret()

    # Generate OTP using the secret key
    otp = generate_otp(secret)

    # Save the secret key and OTP for later verification
    # This is just an example, in a real application, you'd likely store it securely
    users[email] = {
        'secret': secret,
        'otp': otp
    }

    # Send the OTP via email
    send_otp_email(email, otp)

    return jsonify({'message': 'OTP sent successfully'})

@app.route('/verify-otp', methods=['POST'])
def verify_otp_route():
    data = request.get_json()

    if 'email' not in data or 'otp' not in data:
        return jsonify({'error': 'Email and OTP are required'}), 400

    email = data['email']
    user_otp = data['otp']

    # Retrieve the saved secret key and OTP
    user_data = users.get(email)

    if not user_data:
        return jsonify({'error': 'Email not found'}), 400

    secret = user_data['secret']

    # Verify the OTP
    if verify_otp(user_otp, secret):
        return jsonify({'message': 'OTP verification successful'}), 200
    else:
        return jsonify({'error': 'Invalid OTP'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=8080)
