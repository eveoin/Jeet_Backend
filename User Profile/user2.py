from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import json
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_profiles.db'  # SQLite database file
db = SQLAlchemy(app)


class UserProfile(db.Model):
    __tablename__ = 'user_profile'
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))  # Unique ID
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    bio = db.Column(db.String(200), nullable=True)


with app.app_context():
    # Create the database tables
    db.create_all()


@app.route('/create-profile', methods=['POST'])
def create_profile():
    data = request.get_json()

    if 'username' not in data or 'email' not in data:
        return jsonify({'error': 'Username and email are required'}), 400

    username = data['username']
    email = data['email']
    bio = data.get('bio', '')  # Optional bio field

    if UserProfile.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400

    new_profile = UserProfile(username=username, email=email, bio=bio)
    db.session.add(new_profile)
    db.session.commit()

    return jsonify({'message': 'User profile created successfully', 'user_id': new_profile.id}), 201


@app.route('/get-profile/<user_id>', methods=['GET'])
def get_profile(user_id):
    user_profile = db.session.query(UserProfile).get(user_id)

    if user_profile:
        return jsonify({'username': user_profile.username, 'email': user_profile.email, 'bio': user_profile.bio})
    else:
        return jsonify({'error': 'User not found'}), 404


@app.route('/update-profile/<user_id>', methods=['PUT'])
def update_profile(user_id):
    user_profile = db.session.query(UserProfile).get(user_id)

    if user_profile is None:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()

    new_email = data.get('email', user_profile.email)
    new_bio = data.get('bio', user_profile.bio)

    user_profile.email = new_email
    user_profile.bio = new_bio

    db.session.commit()

    return jsonify({'message': 'User profile updated successfully',
                    'username': user_profile.username,
                    'email': user_profile.email,
                    'bio': user_profile.bio}), 200


if __name__ == '__main__':
    app.run(debug=True, port=8080)
