# Cleven's WhatsApp AI Bot

## Overview
Personal AI assistant for WhatsApp, powered by Google Gemini. Responds with Cleven's playful, youth-gen Kiswahili-flavored style.

## Project Structure
```
.
├── src/
│   ├── main.py                # Entry point - Flask app on port 5000
│   ├── app.py                 # Flask webhook endpoints
│   ├── chatbot.py             # Gemini integration
│   └── conversation_memory.py # JSON storage + memory management
├── data/
│   └── conversations/         # JSON files per phone number
├── logs/
│   └── webhook.log            # All activity logs
├── docs/
│   └── USAGE.md               # Detailed usage guide
└── requirements.txt
```

## Running the Application
The app runs on port 5000 via the "WhatsApp Bot API" workflow.

## Required Environment Variables
- `GEMINI_API_KEY` - Google Gemini API key (required)
- `WHAPI_TOKEN` - Whapi.cloud token (optional, for sending replies)
- `WHAPI_BASE_URL` - Whapi base URL (optional)

## API Endpoints
- `GET /` - Health check
- `POST /webhook` - Receive WhatsApp messages and get AI replies
- `POST /clear/<phone_number>` - Clear conversation history for a user

## Tech Stack
- Python 3.11
- Flask (web framework)
- Google Gemini API (AI responses)
- JSON file storage (conversation persistence)
