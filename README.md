<div align="center">

# Personal AI WhatsApp Bot

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.1+-green.svg)](https://flask.palletsprojects.com/)
[![Google Gemini](https://img.shields.io/badge/Google-Gemini%20AI-orange.svg)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()
[![Free Tier](https://img.shields.io/badge/Cost-Free%20Tier-brightgreen.svg)]()

### Personal AI assistant for WhatsApp, powered by Google Gemini
*Responds with Personal AI's playful, youth-gen Kiswahili-flavored style*

</div>

## What This AI Agent Does

This is an intelligent WhatsApp chatbot that acts as **CGM personal AI assistant**. It processes incoming WhatsApp messages via webhook, generates contextual responses using **free Google Gemini models**, and maintains conversation history to provide coherent, personalized interactions.

### Core Capabilities

**1. Message Processing & Response Generation**
- Receives messages from WhatsApp via HTTP webhook (POST /webhook)
- Supports multiple payload formats (simple JSON and Whapi cloud webhooks)
- Uses Google Gemini API (free tier) to generate human-like responses
- **Seamless multi-key fallback**: Configure multiple API keys, system tries all combinations
  - For each API key, tries: `gemini-2.0-flash` → `gemini-2.5-flash` → `gemini-1.5-flash` → `gemini-1.5-pro`
  - When quota expires on one key, automatically switches to next key
  - Resets to primary key after successful request
  - Only shows error if ALL keys × ALL models are exhausted
  - All using Google's free tier with no cost

**2. Conversation Memory & Context**
- Maintains separate conversation history for each phone number/chat ID
- Stores only the **last 4 user-assistant message pairs** (8 messages total + system prompt)
- Minimizes token consumption while preserving recent context
- Persists conversations to **JSON files** in `data/conversations/`
- Each user gets their own file: `data/conversations/{phone_number}.json`
- Sessions auto-expire after 24 hours of inactivity
- History survives bot restarts (loaded from JSON on first access)

**3. CGM Persona & Context**

The AI agent is pre-configured with CGM identity and personality:

```
Name: CGM
Role: Personal AI assistant
Tone: Concise, polished, playful with youth energy
Language: English mixed with light Kiswahili slang
Personality Traits:
  - Helpful and responsive
  - Uses local sayings: "mimi nachoka" (I'm tired), "ntakulokotea mawe" (I'll explain it to you)
  - Youthful, relatable, and culturally aware
  - Respectful but casual
Response Guidelines:
  - Keep replies short and to the point
  - Add humor when appropriate
  - If asked who created you: Answer "God"
  - If asked about relationships/girlfriend: Deflect with humor, avoid serious advice
  - Maintain friendly, supportive energy
```

This context is embedded as the **system prompt** in every conversation, ensuring the AI consistently embodies CGM voice.

**4. Smart Model Fallback**
- Tries the primary model first
- On quota errors (429 RESOURCE_EXHAUSTED), automatically switches to next available model
- Remembers which model worked and uses it for subsequent requests
- Provides clear error messages in Kiswahili if all models fail

**5. Comprehensive Logging**
- All webhook requests logged with timestamps and payloads
- Model API calls tracked with response times and character counts
- Conversation operations (save, load, trim) recorded
- Errors logged with full stack traces
- Logs written to both console and `logs/webhook.log`

### JSON Conversation Format

Each conversation file stores:
```json
{
  "phone_number": "+1234567890",
  "last_activity": "2025-12-18T22:30:00.123456",
  "messages": [
    {"role": "system", "content": "You are CGM personal WhatsApp AI..."},
    {"role": "user", "content": "Mambo vipi?"},
    {"role": "assistant", "content": "Poa sana! Niko ready kukusaidia..."},
    {"role": "user", "content": "Unaweza kunieleza AI?"},
    {"role": "assistant", "content": "Bila shaka! AI ni..."}
  ]
}
```

Only the system message + last 4 Q&A pairs are kept to minimize tokens and API costs.

##  Features

- **Multiple API Keys** - Seamless fallback across multiple Gemini API keys when quota expires
- **Free Gemini Models** - Uses gemini-2.0-flash, gemini-1.5-flash, gemini-1.5-pro (all free tier)
- **Smart Memory** - Remembers last 4 conversation turns per user (optimized for token efficiency)
- **Persistent Storage** - Conversation history saved to JSON files, survives restarts
- **Whapi Ready** - Works with Whapi.cloud webhooks for automatic WhatsApp replies
- **Full Logging** - Detailed logs for debugging webhook and model calls
- **Auto-Fallback** - Tries all API keys × all models before giving up (12+ attempts with 3 keys)
- **Kiswahili Persona** - Custom personality with local slang and cultural awareness
- **Zero Downtime** - Automatic key rotation ensures continuous operation

## Quick Start

### Prerequisites
- Python 3.11 or higher
- Git
- Google Gemini API key (free from [Google AI Studio](https://aistudio.google.com/))
- WhatsApp Business API (optional - via [Whapi.cloud](https://whapi.cloud/))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/cleven12/7ee149.git
   cd 7ee149
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   
   Create a `.env` file:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API key(s):
   ```bash
   # Single key (basic)
   GEMINI_API_KEY=your_key_here
   
   # Multiple keys (recommended for zero downtime)
   GEMINI_API_KEY=key1,key2,key3
   
   # Optional: For automatic WhatsApp replies
   WHAPI_TOKEN=your_whapi_token
   WHAPI_BASE_URL=https://gate.whapi.cloud
   ```

4. **Start the bot**
   ```bash
   # Using the restart script (recommended)
   ./restart.sh
   
   # Or manually
   python src/main.py
   ```

5. **Test locally**
   ```bash
   # Send a test message
   ./test_bot.sh "Mambo vipi?"
   
   # Or use curl
   curl -X POST http://localhost:80/webhook \
     -H "Content-Type: application/json" \
     -d '{"phone_number": "+1234567890", "message": "Hello!"}'
   ```

### Getting Gemini API Keys

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API Key" → "Create API key"
4. Copy the key and add to `.env`
5. (Optional) Repeat with different Google accounts for multiple keys

** Pro Tip**: Use 2-3 API keys for seamless operation. Each free key gets 1500 requests/day!

## Project Structure
```
.
├── src/
│   ├── app.py                 # Flask webhook endpoints
│   ├── chatbot.py             # Gemini integration
│   ├── conversation_memory.py # JSON storage + memory management
│   └── main.py                # Entry point
├── data/
│   └── conversations/         # JSON files per phone number
├── logs/
│   └── webhook.log            # All activity logs
├── docs/
│   └── USAGE.md               # Detailed usage guide
└── requirements.txt
```

## Configuration
Edit `.env`:
```bash
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: For sending replies via Whapi
# WHAPI_TOKEN=your_whapi_token
# WHAPI_BASE_URL=https://gate.whapi.cloud
```

## API Endpoints

### `POST /webhook`
Receive WhatsApp messages and get AI replies.

**Simple format:**
```json
{
  "phone_number": "+1234567890",
  "message": "Mambo vipi?"
}
```

**Whapi format:**
```json
{
  "from": "+1234567890",
  "text": "Mambo vipi?"
}
```

**Response:**
```json
{
  "status": "success",
  "response": "Poa sana! Niko ready kukusaidia. Unauliza nini?"
}
```

### `POST /clear/<phone_number>`
Clear conversation history for a user.

**Example:**
```bash
curl -X POST http://localhost:80/clear/+1234567890
```

## Persona

The AI embodies CGM's personal style:
-  Concise, polished, playful tone
-  Light Kiswahili slang ("mimi nachoka", "ntakulokotea mawe", "ipo sawa")
-  Deflects relationship advice with humor
-  Says "God" when asked who created it
-  Professional on ICT topics, casual on social topics

## Documentation

- **[USAGE.md](docs/USAGE.md)** - Detailed usage guide, Whapi integration, testing
- **[MULTI_KEY_SETUP.md](docs/MULTI_KEY_SETUP.md)** - Complete guide to multiple API keys

## Monitoring & Logs

Watch live logs:
```bash
# All webhook activity
tail -f logs/webhook.log

# Filter for errors only
tail -f logs/webhook.log | grep ERROR

# Monitor key switching
tail -f logs/webhook.log | grep "Switched to API key"
```

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [Google Gemini AI](https://ai.google.dev/) - Free AI models
- [Whapi.cloud](https://whapi.cloud/) - WhatsApp Business API
- [Flask](https://flask.palletsprojects.com/) - Web framework

---

<div align="center">
  
**Made with ❤️ for seamless WhatsApp AI conversations**

[Report Bug](https://github.com/cleven12/7ee149/issues) · [Request Feature](https://github.com/cleven12/7ee149/issues)

</div>
