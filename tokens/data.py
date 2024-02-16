from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
api = Api(app)

# Set up the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this to a secure secret key in a production environment
jwt = JWTManager(app)

# In-memory user dictionary for demonstration purposes (replace with a real database in production)
users = {}

class RegisterUser(Resource):
    def post(self):
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')

        if username in users:
            return jsonify({'message': 'User already exists'}), 400

        # For demonstration purposes, you may want to hash the password in a real-world scenario
        users[username] = {'password': password}
        return jsonify({'message': 'User registered successfully'}), 201

class SignUp(Resource):
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        # You can now use the identity of the current user to perform actions
        return jsonify(logged_in_as=current_user), 200

api.add_resource(RegisterUser, '/register')
api.add_resource(SignUp, '/signup')

if __name__ == '__main__':
    app.run(debug=True, port=808)
