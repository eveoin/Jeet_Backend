from flask import Flask, request, jsonify
import uuid
import hashlib
import time

app = Flask(__name__)

users = {}
tokens = {}
verified_tokens = set()
reset_tokens = {}  # New dictionary to store reset tokens
SECRET_KEY = "secretary"
TOKEN_EXPIRATION_SECONDS = 300


def generate_token(username):
    token_data = username + SECRET_KEY
    token = hashlib.sha256(token_data.encode()).hexdigest()
    tokens[token] = time.time() + TOKEN_EXPIRATION_SECONDS
    return token


def is_token_valid(token):
    return token in tokens and tokens[token] > time.time()


def generate_reset_token(username):
    reset_token = str(uuid.uuid4())
    return reset_token


@app.route('/signup', methods=['POST'])
def sign_up():
    data = request.get_json()

    if 'username' not in data or 'password' not in data or 'email' not in data:
        return jsonify({'error': 'Username, password, and email are required'}), 400

    username = data['username']
    password = data['password']
    email = data['email']

    if username in users:
        return jsonify({'error': 'Username already exists'}), 400

    users[username] = {'password': password, 'email': email}

    return jsonify({'message': 'User signed up successfully'}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password are required'}), 400

    username = data['username']
    password = data['password']

    if username not in users or users[username]['password'] != password:
        return jsonify({'error': 'Invalid credentials'}), 401

    token = generate_token(username)
    return jsonify({'token': token}), 200


@app.route('/verify', methods=['POST'])
def verify_token():
    data = request.get_json()

    if 'token' not in data:
        return jsonify({'error': 'Token is required'}), 400

    token = data['token']

    if token in verified_tokens:
        return jsonify({'message': 'Token has already been verified'}), 200

    for username, user_data in users.items():
        if generate_token(username) == token and is_token_valid(token):
            password = user_data['password']

            with open('token_verify.txt', 'a') as file:
                file.write(
                    f"User Name: {username},\nPassword: {password}, \nToken: {token}, \nExpiration Time: {tokens[token]}\n\n\n")

            verified_tokens.add(token)

            return jsonify({'message': 'Token is valid'}), 200

    return jsonify({'error': 'Invalid token'}), 401


@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()

    if 'email' not in data:
        return jsonify({'error': 'Email is required'}), 400

    email = data['email']

    username = next((user for user, data in users.items() if data['email'] == email), None)

    if username:
        reset_token = generate_reset_token(username)
        reset_tokens[reset_token] = username

        # Send the reset token to the user via email (in a real-world scenario)

        return jsonify({'message': 'Reset token generated successfully'}), 200
    else:
        return jsonify({'error': 'Email not found'}), 404


@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()

    if 'token' not in data or 'new_password' not in data:
        return jsonify({'error': 'Token and new_password are required'}), 400

    reset_token = data['token']
    new_password = data['new_password']

    username = reset_tokens.get(reset_token)

    if username:
        users[username]['password'] = new_password

        # Remove the reset token from the dictionary (optional)
        del reset_tokens[reset_token]

        return jsonify({'message': 'Password reset successfully'}), 200
    else:
        return jsonify({'error': 'Invalid or expired token'}), 401


if __name__ == '__main__':
    app.run(debug=True, port=808)

