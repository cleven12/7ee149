from flask import Flask, request, jsonify
from dotenv import load_dotenv
import logging
from datetime import datetime
from chatbot import WhatsAppChatbot

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/webhook.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

myapp = Flask(__name__)

# Initialize chatbot
chatbot = WhatsAppChatbot()


def _extract_incoming_payload(data: dict):
    """
    Normalize inbound payloads.

    Supports the simple shape used in docs:
        {"phone_number": "+123", "message": "hi"}

    And common fields from Whapi webhooks (see https://whapi.cloud/docs):
        {"from": "+123", "text": "hi"}
        {"messages": [{"from": "+123", "text": "hi"}]}
    """
    if not data:
        return None, None

    phone_number = (
        data.get("phone_number")
        or data.get("from")
        or data.get("sender")
        or data.get("chatId")
        or data.get("chat_id")
        or data.get("phone")
    )

    user_message = (
        data.get("message")
        or data.get("text")
        or data.get("body")
        or data.get("msg")
    )

    if (not phone_number or not user_message) and isinstance(data.get("messages"), list):
        first = data["messages"][0] if data["messages"] else {}
        phone_number = phone_number or first.get("from") or first.get("sender") or first.get("chatId")
        user_message = user_message or first.get("text") or first.get("body")

    return phone_number, user_message


@myapp.route('/')
def main():
    return "WhatsApp Chatbot API - Running"


@myapp.route('/webhook', methods=['POST'])
def webhook():
    """
    Webhook endpoint for receiving WhatsApp messages.

    Accepts both the simple JSON shape used in this repo and common Whapi webhook
    fields. Minimum required: a phone/chat identifier and the message text.
    """
    request_time = datetime.now().isoformat()
    logger.info(f"[WEBHOOK] Received POST request at {request_time}")
    
    try:
        data = request.get_json()
        logger.info(f"[WEBHOOK] Raw payload: {data}")

        phone_number, user_message = _extract_incoming_payload(data)
        logger.info(f"[WEBHOOK] Extracted - Phone: {phone_number}, Message: {user_message}")

        if not phone_number or not user_message:
            logger.warning(f"[WEBHOOK] Missing required fields - Phone: {phone_number}, Message: {user_message}")
            return jsonify({"error": "Missing phone_number or message"}), 400

        # Process message and get response
        logger.info(f"[WEBHOOK] Processing message for {phone_number}")
        response = chatbot.process_message(phone_number, user_message)
        logger.info(f"[WEBHOOK] Response generated for {phone_number}: {response[:100]}...")

        return jsonify({
            "phone_number": phone_number,
            "response": response,
            "status": "success"
        }), 200
    
    except Exception as e:
        logger.error(f"[WEBHOOK] Error processing request: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@myapp.route('/clear/<phone_number>', methods=['POST'])
def clear_history(phone_number):
    """Clear conversation history for a phone number"""
    logger.info(f"[CLEAR] Clearing history for {phone_number}")
    try:
        chatbot.clear_conversation(phone_number)
        logger.info(f"[CLEAR] Successfully cleared history for {phone_number}")
        return jsonify({
            "message": f"Conversation cleared for {phone_number}",
            "status": "success"
        }), 200
    except Exception as e:
        logger.error(f"[CLEAR] Error clearing history for {phone_number}: {str(e)}")
        return jsonify({"error": str(e)}), 500
