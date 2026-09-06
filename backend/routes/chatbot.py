from flask import Blueprint, request
from backend.database import get_db
from backend.services.chatbot_service import ChatbotService
from backend.models.notification import Notification
from backend.utils.responses import success_response, error_response

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/api')

@chatbot_bp.route('/chatbot/intents', methods=['GET'])
def get_intents():
    return success_response(data=ChatbotService.get_intents(), message="FAQ intents retrieved.")

@chatbot_bp.route('/chatbot/query', methods=['POST'])
def query_chatbot():
    data = request.get_json() or {}
    q = data.get('query', '')
    if not q:
        return error_response("Query cannot be empty.", error_code="VALIDATION_ERROR")

    res = ChatbotService.answer_query(q)
    return success_response(data=res, message="Answer retrieved.")

@chatbot_bp.route('/notifications/<string:farmer_id>', methods=['GET'])
def get_notifications(farmer_id: str):
    db = next(get_db())
    notifications = (
        db.query(Notification)
        .filter(Notification.farmer_id == farmer_id)
        .order_by(Notification.sent_at.desc())
        .limit(20)
        .all()
    )
    return success_response(data=[n.to_dict() for n in notifications], message="Notifications retrieved.")
