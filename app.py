from datetime import datetime, timezone
import logging
import re
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True, nullable=False, index=True )
    nickname = db.Column(db.String(50), nullable=False, unique=True, index=True)
    phone = db.Column(db.String(20), nullable=False, unique=True, index=True)
    email = db.Column(db.String(100), nullable=False, unique=True, index=True)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self) -> str:
        return f'<User {self.nickname}>,<Phone {self.phone}>,<Email {self.email}>,<message {self.message}>'
def is_valid_email(email):
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None
@app.route('/api/save_user_info', methods=['POST'])
def save_user_info():
    try:
        data = request.json
        required_fields = ['nickname', 'phone', 'email', 'message']
        for item in required_fields:
            if item not in data or not data[item]:
                return jsonify({'error': f'{item}不能为空'}),400
        if not is_valid_email(data['email']):
            return jsonify({'error': '邮箱格式不正确'}),400
        existing_user = User.query.filter(
    (User.nickname == data['nickname']) |
    (User.phone == data['phone']) |
    (User.email == data['email'])
).first()
        if existing_user:
            if existing_user.nickname == data['nickname']:
                return jsonify({'error': '用户昵称已存在'}), 400
            elif existing_user.phone == data['phone']:
                return jsonify({'error': '手机号已存在'}), 400
            elif existing_user.email == data['email']:
                return jsonify({'error': '邮箱已存在'}), 400
        user = User(nickname=data['nickname'], phone=data['phone'], email=data['email'], message=data['message'])   
        db.session.add(user)
        db.session.commit()
        return {'success': '用户信息保存成功', "user_id": user.id, "code": "201"}, 201
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return jsonify({'error': '服务器内部错误'}),500

@app.route('/api/get_user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try :
        user = User.query.get(user_id)
        if user:
            return jsonify({'id': user_id, 'nickname': user.nickname, "phone": user.phone, "email": user.email, "message": user.message, "created_at": user.created_at}),200
        return jsonify({'error': '用户不存在'}),404
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return jsonify({'error': '服务器内部错误'}),500
    
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)   