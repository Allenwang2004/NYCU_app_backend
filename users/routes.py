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

@users_bp.route('/log', methods=['POST'])
@jwt_required()
def add_or_update_log():
    """
    新增或更新心情與日記紀錄 (需要 JWT)
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
            diary:
              type: string
              example: "今天過得很好！"
    responses:
      200:
        description: 紀錄新增或更新成功
    """
    user_id = get_jwt_identity()
    data = request.json

    log_date = datetime.strptime(data.get('date'), '%Y-%m-%d').date()
    mood = data.get('mood')
    diary = data.get('diary')

    log = MoodLog.query.filter_by(user_id=user_id, date=log_date).first()
    if log:
        # 已存在：更新
        if mood is not None:
            log.mood = mood
        if diary is not None:
            log.diary = diary
    else:
        # 不存在：新增
        log = MoodLog(user_id=user_id, date=log_date, mood=mood or '', diary=diary or '')
        db.session.add(log)

    db.session.commit()
    return jsonify({'msg': '紀錄成功'}), 200

@users_bp.route('/log', methods=['GET'])
@jwt_required()
def get_all_logs():
    """
    取得使用者所有心情與日記紀錄 (需要 JWT)
    ---
    tags:
      - Users
    security:
      - Bearer: []
    responses:
      200:
        description: 回傳所有紀錄列表
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
                  diary:
                    type: string
                    example: "今天過得很好！"
    """
    user_id = get_jwt_identity()
    logs = MoodLog.query.filter_by(user_id=user_id).order_by(MoodLog.date.desc()).all()
    result = [
        {
            'date': log.date.isoformat(),
            'mood': log.mood,
            'diary': log.diary
        }
        for log in logs
    ]
    return jsonify({'logs': result})