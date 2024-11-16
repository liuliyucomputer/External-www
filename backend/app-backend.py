from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  # 导入 CORS
from datetime import datetime
import re
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)

# 初始化 Flask 应用
app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 定义用户模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(50), nullable=False, unique=True)  # 添加unique=True来确保昵称唯一
    phone = db.Column(db.String(20), nullable=False, unique=True)      # 添加unique=True来确保电话唯一
    email = db.Column(db.String(100), nullable=False, unique=True)     # 添加unique=True来确保邮箱唯一
    message = db.Column(db.Text, nullable=False)                       # 修改为必填
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.nickname}>'

# 简单的邮箱格式验证
def is_valid_email(email):
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

# 统一的保存接口
@app.route('/api/save_user_info', methods=['POST'])
def save_user_info():
    try:
        data = request.json

        # 验证必填字段
        required_fields = ['nickname', 'phone', 'email', 'message']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"{field} 是必填字段"}), 400

        # 验证邮箱格式
        if not is_valid_email(data['email']):
            return jsonify({"error": "邮箱格式不正确"}), 400
        
        # 检查是否已存在相同的用户信息
        if User.query.filter_by(nickname=data['nickname']).first():
            return jsonify({"error": "昵称已存在"}), 400

        if User.query.filter_by(phone=data['phone']).first():
            return jsonify({"error": "电话已存在"}), 400

        if User.query.filter_by(email=data['email']).first():
            return jsonify({"error": "邮箱已存在"}), 400

        # 创建新用户并一次性保存所有信息
        user = User(
            nickname=data['nickname'],
            phone=data['phone'],
            email=data['email'],
            message=data['message']
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({
            "message": "用户信息保存成功",
            "user_id": user.id
        }), 201

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return jsonify({"error": "服务器内部错误"}), 500

# 查询用户信息接口
@app.route('/api/get_user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = User.query.get(user_id)
        if user:
            return jsonify({
                "id": user.id,
                "nickname": user.nickname,
                "phone": user.phone,
                "email": user.email,
                "message": user.message,
                "created_at": user.created_at.isoformat()
            }), 200
        return jsonify({"error": "用户不存在"}), 404
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return jsonify({"error": "服务器内部错误"}), 500

# 主程序
if __name__ == '__main__':
    # 创建数据库表
    with app.app_context():
        db.create_all()
    # 启动应用
    app.run(debug=True)
