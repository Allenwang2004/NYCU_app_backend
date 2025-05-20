from flask import jsonify
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import User, MoodLog
from datetime import datetime
from . import users_bp

@users_bp.route('/check_is_filled', methods=['GET'])
@jwt_required()
def check_is_filled():
    """
    Check if user profile is filled (需要 JWT)
    ---
    tags:
      - Users
    security:
      - Bearer: []
    responses:
      200:
        description: 回傳 is_filled 狀態
        schema:
          type: object
          properties:
            is_filled:
              type: boolean
              example: true
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': '找不到使用者'}), 400

    return jsonify({'is_filled': user.is_filled})

@users_bp.route('/set_is_filled', methods=['POST'])
@jwt_required()
def set_is_filled():
    """
    Set user is_filled to True (需要 JWT)
    ---
    tags:
      - Users
    security:
      - Bearer: []
    responses:
      200:
        description: 成功設為 True
        schema:
          type: object
          properties:
            msg:
              type: string
              example: 已設為填寫完成
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': '找不到使用者'}), 400

    user.is_filled = True
    db.session.commit()
    return jsonify({'msg': '已設為填寫完成'})

@users_bp.route('/mood', methods=['POST'])
@jwt_required()
def add_mood_log():
    """
    新增心情紀錄 (需要 JWT)
    ---
    tags:
      - Users
    security:
      - Bearer: []
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            date:
              type: string
              example: "2025-05-07"
            mood:
              type: string
              example: "開心"
    responses:
      201:
        description: 新增成功
    """
    user_id = get_jwt_identity()
    data = request.json
    mood_date = datetime.strptime(data.get('date'), '%Y-%m-%d').date()
    mood_text = data.get('mood', '')

    new_log = MoodLog(user_id=user_id, date=mood_date, mood=mood_text)
    db.session.add(new_log)
    db.session.commit()

    return jsonify({'msg': '新增成功'}), 201

@users_bp.route('/mood', methods=['GET'])
@jwt_required()
def get_mood_logs():
    """
    取得使用者所有心情紀錄 (需要 JWT)
    ---
    tags:
      - Users
    security:
      - Bearer: []
    responses:
      200:
        description: 回傳心情紀錄列表
        schema:
          type: object
          properties:
            logs:
              type: array
              items:
                type: object
                properties:
                  date:
                    type: string
                    example: "2025-05-07"
                  mood:
                    type: string
                    example: "開心"
    """
    user_id = get_jwt_identity()
    logs = MoodLog.query.filter_by(user_id=user_id).all()
    result = [{'date': log.date.isoformat(), 'mood': log.mood} for log in logs]
    return jsonify({'logs': result})