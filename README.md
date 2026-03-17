<div align="center">

# WhatsApp AI Bot

**Personal AI assistant for WhatsApp, powered by Google Gemini**

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1+-green.svg)
![Gemini](https://img.shields.io/badge/Google-Gemini%20AI-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Free](https://img.shields.io/badge/Cost-Free%20Tier-brightgreen.svg)

</div>

---

## Overview

A Flask-based WhatsApp chatbot that processes incoming messages via webhook and responds using Google Gemini AI. Built around a custom **CGM persona** — concise, playful, Kiswahili-flavored tone for personal use.

---

## Features

| Feature | Description |
|---|---|
| **Multi-key fallback** | Rotates across multiple Gemini API keys automatically on quota exhaustion |
| **Smart memory** | Stores last 4 conversation turns per user, persisted to JSON |
| **Whapi integration** | Native support for Whapi.cloud webhook format |
| **Auto model fallback** | Tries `gemini-2.0-flash` → `gemini-2.5-flash` → `gemini-1.5-flash` → `gemini-1.5-pro` |
| **Session expiry** | Conversations auto-expire after 24 hours of inactivity |
| **Full logging** | Console + file logging (`logs/webhook.log`) |

---

## Project Structure
```
.
├── src/
│   ├── app.py                  # Webhook endpoints
│   ├── chatbot.py              # Gemini integration + model fallback
│   ├── conversation_memory.py  # JSON storage + session management
│   └── main.py                 # Entry point
├── data/conversations/         # Per-user conversation history
├── logs/webhook.log            # Activity logs
└── docs/                       # Extended documentation
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- Gemini API key — [Get one free from Google AI Studio](https://aistudio.google.com/)
- *(Optional)* [Whapi.cloud](https://whapi.cloud/) token for sending replies

### Setup
```bash
git clone https://github.com/cleven12/7ee149.git
cd 7ee149
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:
```env
# Single key
GEMINI_API_KEY=your_key_here

# Multiple keys (recommended — each gets 1500 free requests/day)
GEMINI_API_KEY=key1,key2,key3

# Optional: auto-reply via Whapi
WHAPI_TOKEN=your_whapi_token
WHAPI_BASE_URL=https://gate.whapi.cloud
```

### Run
```bash
python src/main.py
```

### Test
```bash
curl -X POST http://localhost:80/webhook \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+255700000000", "message": "Mambo vipi?"}'
```

---

## API Reference

### `POST /webhook`

Accepts two formats:

**Simple:**
```json
{ "phone_number": "+255700000000", "message": "Mambo vipi?" }
```

**Whapi:**
```json
{ "from": "+255700000000", "text": "Mambo vipi?" }
```

**Response:**
```json
{ "status": "success", "response": "Poa sana! Unauliza nini?" }
```

### `POST /clear/<phone_number>`

Clears conversation history for a specific user.

---

## Persona

The bot runs as **CGM** — a personal AI with a defined character:

- Concise and to the point
- Light Kiswahili slang (`mimi nachoka`, `ipo sawa`, `ntakulokotea mawe`)
- Deflects relationship questions with humor
- Professional on tech topics, casual on everything else

---

## Logs
```bash
tail -f logs/webhook.log               # Live activity
tail -f logs/webhook.log | grep ERROR  # Errors only
tail -f logs/webhook.log | grep "Switched to API key"  # Key rotation
```

---

## License

MIT — see [LICENSE](LICENSE).

---

<div align="center">
 
**Made with ❤️ for seamless WhatsApp AI conversations**

[Report Bug](https://github.com/cleven12/7ee149/issues) · [Request Feature](https://github.com/cleven12/7ee149/issues) 
</div>
