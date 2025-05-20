from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import questionnaire_bp
from ollama_agent import OllamaMultiTurnAgent

agent_session = {}

@questionnaire_bp.route('/start', methods=['POST'])
@jwt_required()
def start_questionnaire():
    """
    啟動問卷流程 (需要 JWT)
    ---
    tags:
      - Questionnaire
    security:
      - Bearer: []
    responses:
      200:
        description: 啟動成功並回傳第一題
        schema:
          type: object
          properties:
            question:
              type: string
              example: 您最近偏好在室內還是戶外活動？
    """
    user_id = get_jwt_identity()
    agent_session[user_id] = OllamaMultiTurnAgent()
    first_question = agent_session[user_id].get_next_question()
    return jsonify({'question': first_question})

@questionnaire_bp.route('/next', methods=['POST'])
@jwt_required()
def next_question():
    """
    回答一題後取得下一題 (需要 JWT)
    ---
    tags:
      - Questionnaire
    security:
      - Bearer: []
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            answer:
              type: string
              example: 我喜歡安靜的室內空間
    responses:
      200:
        description: 回傳下一題
        schema:
          type: object
          properties:
            question:
              type: string
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    if user_id not in agent_session:
        return jsonify({'msg': '請先啟動問卷流程'}), 400
    answer = data.get('answer', '')
    question = agent_session[user_id].get_next_question(user_answer=answer)
    return jsonify({'question': question})

@questionnaire_bp.route('/summary', methods=['GET'])
@jwt_required()
def summarize_questionnaire():
    """
    完成問卷後產出活動推薦 (需要 JWT)
    ---
    tags:
      - Questionnaire
    security:
      - Bearer: []
    responses:
      200:
        description: 回傳推薦活動列表
        schema:
          type: object
          properties:
            recommendation:
              type: string
              example: 我建議你選擇閱讀，因為你喜歡靜態、室內且時間有限的活動。
    """
    user_id = get_jwt_identity()
    if user_id not in agent_session:
        return jsonify({'msg': '尚未開始問卷'}), 400
    summary = agent_session[user_id].summarize_recommendation()
    del agent_session[user_id]
    return jsonify({'recommendation': summary})