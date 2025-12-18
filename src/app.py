from flask import Flask, request, jsonify
from dotenv import load_dotenv
import logging
import os
import requests
from datetime import datetime
from chatbot import WhatsAppChatbot

load_dotenv()

# Configure logging - use path relative to project root
import pathlib
log_dir = pathlib.Path(__file__).parent.parent / 'logs'
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'webhook.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

myapp = Flask(__name__)

# Initialize chatbot
chatbot = WhatsAppChatbot()

# Whapi configuration
WHAPI_TOKEN = os.getenv("WHAPI_TOKEN")
WHAPI_BASE_URL = os.getenv("WHAPI_BASE_URL", "https://gate.whapi.cloud")


def send_whapi_reply(chat_id: str, message: str) -> bool:
    """
    Send a reply via Whapi API.
    
    Args:
        chat_id: WhatsApp chat ID (phone number with @s.whatsapp.net or group ID)
        message: Text message to send
    
    Returns:
        True if sent successfully, False otherwise
    """
    if not WHAPI_TOKEN:
        logger.warning("[WHAPI] WHAPI_TOKEN not configured, skipping reply")
        return False
    
    try:
        # Ensure chat_id has proper format
        if not "@" in chat_id:
            chat_id = f"{chat_id}@s.whatsapp.net"
        
        url = f"{WHAPI_BASE_URL}/messages/text"
        headers = {
            "Authorization": f"Bearer {WHAPI_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "to": chat_id,
            "body": message
        }
        
        logger.info(f"[WHAPI] Sending reply to {chat_id}: {message[:50]}...")
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200 or response.status_code == 201:
            logger.info(f"[WHAPI] Reply sent successfully to {chat_id}")
            return True
        else:
            logger.error(f"[WHAPI] Failed to send reply: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"[WHAPI] Error sending reply: {str(e)}", exc_info=True)
        return False


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
        
        # Extract text - handle nested structure like {"text": {"body": "message"}}
        text_field = user_message or first.get("text") or first.get("body")
        if isinstance(text_field, dict):
            user_message = text_field.get("body") or text_field.get("text") or str(text_field)
        else:
            user_message = text_field

    # Final check: if message is still a dict, try to extract body
    if isinstance(user_message, dict):
        user_message = user_message.get("body") or user_message.get("text") or str(user_message)

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

        # Send reply back via Whapi (if configured)
        reply_sent = send_whapi_reply(phone_number, response)

        return jsonify({
            "phone_number": phone_number,
            "response": response,
            "reply_sent": reply_sent,
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
