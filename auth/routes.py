from flask import request, jsonify, render_template, current_app
from flask_mail import Message
from flask_jwt_extended import create_access_token
from itsdangerous import URLSafeTimedSerializer
import re

from . import auth_bp
from extensions import db, mail
from models import User

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    User Register
    ---
    tags:
      - Auth
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              example: user@example.com
            password:
              type: string
              example: "Abc123@!"
            name:
              type: string
              example: 王小明
    responses:
      201:
        description: 註冊成功
      400:
        description: 格式錯誤
    """
    data = request.json
    email = data.get('email', '').strip()
    password = data.get('password', '')
    name = data.get('name', '').strip()

    # 驗證 email 格式
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_pattern, email):
        return jsonify({'msg': '請輸入有效的 email'}), 400

    # 驗證密碼強度
    if (len(password) < 8 or
        not re.search(r'[A-Z]', password) or
        not re.search(r'[a-z]', password) or
        not re.search(r'[\W_]', password)):
        return jsonify({'msg': '密碼需包含大小寫英文字母與特殊符號，且長度不少於 8 位'}), 400

    # 檢查是否已註冊
    if User.query.filter_by(email=email).first():
        return jsonify({'msg': '此 email 已被註冊'}), 400

    # 建立帳號
    user = User(email=email, password=password, name=name)
    db.session.add(user)
    db.session.commit()

    # 發送驗證信
    s = URLSafeTimedSerializer(current_app.config['JWT_SECRET_KEY'])
    token = s.dumps(user.email, salt='email-confirm')
    link = f"http://140.113.26.107:5000/auth/verify/{token}"
    msg = Message('驗證你的帳號', sender=current_app.config['MAIL_USERNAME'], recipients=[user.email])
    msg.html = render_template('verify_email.html', link=link, name=name)
    mail.send(msg)

    return jsonify({'msg': '註冊成功，請到信箱收信完成驗證'}), 201

@auth_bp.route('/verify/<token>', methods=['GET'])
def verify_email(token):
    """
    Email Verification
    ---
    tags:
      - Auth
    parameters:
      - name: token
        in: path
        required: true
        type: string
        description: 驗證連結中的 token
    responses:
      200:
        description: 驗證成功後返回成功頁面
        content:
          text/html:
            example: "<h1>驗證成功</h1>"
      400:
        description: 驗證失敗或連結過期
        content:
          text/html:
            example: "<h1>驗證失敗</h1>"
    """
    s = URLSafeTimedSerializer(current_app.config['JWT_SECRET_KEY'])
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except Exception:
        return render_template('verify_failed.html', reason="驗證連結無效或已過期")

    user = User.query.filter_by(email=email).first()
    if not user:
        return render_template('verify_failed.html', reason="找不到使用者")

    user.is_verified = True
    db.session.commit()
    return render_template('verify_success.html')

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login
    ---
    tags:
      - Auth
    consumes:
      - application/json
    parameters:
      - name: email
        in: body
        required: true
        type: string
        schema:
          type: object
          properties:
            email:
              type: string
              example: user@example.com
            password:
              type: string
              example: "123456"
    responses:
      200:
        description: 成功登入並取得 token
        schema:
          type: object
          properties:
            token:
              type: string
      401:
        description: 帳號或密碼錯誤
    """
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'msg': '帳號或密碼錯誤'}), 401
    if not user.is_verified:
        return jsonify({'msg': '請先完成信箱驗證'}), 403
    token = create_access_token(identity=user.id)
    return jsonify({'token': token})