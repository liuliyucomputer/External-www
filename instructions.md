使用说明：

1. 双击运行 app.exe
2. 打开浏览器，访问 http://localhost:5000
3. 使用 POST 请求发送数据到 http://localhost:5000/api/save_user_info
4. 使用 GET 请求查询用户信息：http://localhost:5000/api/get_user/<user_id>

示例 POST 请求数据格式：
{
"nickname": "测试用户",
"phone": "13800138000",
"email": "test@example.com",
"message": "这是测试信息"
}

注意：首次运行时会在程序所在目录创建 users.db 数据库文件。
作者:liuliyu 联系方式
邮箱:1605010842@qq.com
