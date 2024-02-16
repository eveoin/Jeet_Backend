from flask import Flask, jsonify, request
import jwt
import json
import datetime

app = Flask(__name__)

SECRET_KEY = 'your_secret_key'

sample_user = {}


@app.route('/login', methods=['POST'])
def login():

    # Get user credentials from the request data
    user_data = request.json  # Assuming the request data is in JSON format
    user_id = user_data.get('user_id')
    email = user_data.get('email')

    if not user_id or not email:
        return jsonify({'message': 'User credentials are missing!'}), 400

    sample_user['user_id'] = user_id
    sample_user['email'] = email

    token_payload = {
        'user_id': sample_user['user_id'],
        'email': sample_user['email'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1)
    }

    token = jwt.encode(token_payload, SECRET_KEY, algorithm='HS256')

    with open('my_token.txt', 'a') as file:
        file.write(f"User ID: {sample_user['user_id']}, \nEmail: {sample_user['email']}, \nToken: {token}\n\n\n")

    return jsonify({'token': token})


@app.route('/protected', methods=['GET'])
def protected_route():
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'message': 'Authentication Token is missing!'}), 401

    try:
        decoded_token = jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=['HS256'])

        return jsonify({'message': 'You have access to the protected route!'})
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired!'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid Token!'}), 401


if __name__ == '__main__':
    app.run(debug=True, port=8080)
