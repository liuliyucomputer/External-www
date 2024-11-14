from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/api/save_nickname', methods=['POST'])
def save_nickname():
    nickname = request.json.get('nickname')
    user = User(nickname=nickname)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Nickname saved successfully"}), 201

@app.route('/api/save_phone', methods=['POST'])
def save_phone():
    phone = request.json.get('phone')
    user_id = request.json.get('user_id')
    user = User.query.get(user_id)
    if user:
        user.phone = phone
        db.session.commit()
        return jsonify({"message": "Phone number saved successfully"}), 200
    return jsonify({"error": "User not found"}), 404

@app.route('/api/save_email', methods=['POST'])
def save_email():
    email = request.json.get('email')
    user_id = request.json.get('user_id')
    user = User.query.get(user_id)
    if user:
        user.email = email
        db.session.commit()
        return jsonify({"message": "Email saved successfully"}), 200
    return jsonify({"error": "User not found"}), 404

@app.route('/api/save_message', methods=['POST'])
def save_message():
    message = request.json.get('message')
    user_id = request.json.get('user_id')
    user = User.query.get(user_id)
    if user:
        user.message = message
        db.session.commit()
        return jsonify({"message": "Message saved successfully"}), 200
    return jsonify({"error": "User not found"}), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)