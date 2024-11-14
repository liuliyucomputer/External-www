from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 定义用户模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.nickname}>'

# 统一的保存接口
@app.route('/api/save_user_info', methods=['POST'])
def save_user_info():
    try:
        data = request.json
        
        # 创建新用户并一次性保存所有信息
        user = User(
            nickname=data.get('nickname'),
            phone=data.get('phone'),
            email=data.get('email'),
            message=data.get('message')
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            "message": "用户信息保存成功",
            "user_id": user.id
        }), 201
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
        return jsonify({"error": str(e)}), 500

# 主程序
if __name__ == '__main__':
    # 创建数据库表
    with app.app_context():
        db.create_all()
    # 启动应用
    app.run(debug=True)