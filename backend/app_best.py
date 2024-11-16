from datetime import datetime, timezone
import logging
import re
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import bleach
from werkzeug.security import generate_password_hash

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])
limiter.init_app(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True, nullable=False, index=True)
    nickname = db.Column(db.String(50), nullable=False, unique=True, index=True)
    phone = db.Column(db.String(256), nullable=False, unique=True, index=True)  # 加密存储
    email = db.Column(db.String(100), nullable=False, unique=True, index=True)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

def is_valid_email(email):
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

def is_valid_phone(phone):
    regex = r'^\d{11}$'  # 假设手机号为11位数字
    return re.match(regex, phone) is not None

@app.route('/api/save_user_info', methods=['POST'])
@limiter.limit("5 per minute")
def save_user_info():
    try:
        data = request.json
        required_fields = ['nickname', 'phone', 'email', 'message']
        for item in required_fields:
            if item not in data or not data[item]:
                return jsonify({'error': f'{item}不能为空'}), 400
        
        if not is_valid_email(data['email']):
            return jsonify({'error': '邮箱格式不正确'}), 400
        
        if not is_valid_phone(data['phone']):
            return jsonify({'error': '手机号格式不正确'}), 400

        existing_user = User.query.filter(
            (User.nickname == data['nickname']) |
            (User.phone == data['phone']) |  # 这里不应该加密
            (User.email == data['email'])
        ).first()

        if existing_user:
            if existing_user.nickname == data['nickname']:
                return jsonify({'error': '用户昵称已存在'}), 400
            elif existing_user.phone == data['phone']:
                return jsonify({'error': '手机号已存在'}), 400
            elif existing_user.email == data['email']:
                return jsonify({'error': '邮箱已存在'}), 400

        user = User(
            nickname=bleach.clean(data['nickname']),
            phone=generate_password_hash(data['phone']),
            email=bleach.clean(data['email']),
            message=bleach.clean(data['message'])
        )
        db.session.add(user)
        db.session.commit()
        return {'success': '用户信息保存成功', "user_id": user.id, "code": "201"}, 201
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return jsonify({'error': '服务器内部错误'}), 500

@app.route('/api/get_user/<int:user_id>', methods=['GET'])
@limiter.limit("10 per minute")
def get_user(user_id):
    try:
        user = User.query.get(user_id)
        if user:
            return jsonify({
                'id': user_id,
                'nickname': user.nickname,
                "email": user.email,
                "message": user.message,
                "created_at": user.created_at
            }), 200
        return jsonify({'error': '用户不存在'}), 404
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return jsonify({'error': '服务器内部错误'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False) 
