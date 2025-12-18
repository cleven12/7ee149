# Cleven's WhatsApp AI Bot

Personal AI assistant for WhatsApp, powered by Google Gemini. Responds with Cleven's playful, youth-gen Kiswahili-flavored style.

## What This AI Agent Does

This is an intelligent WhatsApp chatbot that acts as **Cleven's personal AI assistant**. It processes incoming WhatsApp messages via webhook, generates contextual responses using **free Google Gemini models**, and maintains conversation history to provide coherent, personalized interactions.

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

**3. Cleven's Persona & Context**

The AI agent is pre-configured with Cleven's identity and personality:

```
Name: Cleven
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

This context is embedded as the **system prompt** in every conversation, ensuring the AI consistently embodies Cleven's voice.

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
    {"role": "system", "content": "You are Cleven's personal WhatsApp AI..."},
    {"role": "user", "content": "Mambo vipi?"},
    {"role": "assistant", "content": "Poa sana! Niko ready kukusaidia..."},
    {"role": "user", "content": "Unaweza kunieleza AI?"},
    {"role": "assistant", "content": "Bila shaka! AI ni..."}
  ]
}
```

Only the system message + last 4 Q&A pairs are kept to minimize tokens and API costs.

## Features
- **Multiple API Keys** - Seamless fallback across multiple Gemini API keys when quota expires
- **Free Gemini Models** - Uses gemini-2.0-flash, gemini-1.5-flash, gemini-1.5-pro (all free tier)
- **Smart Memory** - Remembers last 4 conversation turns per user
- **Persistent** - Conversation history saved to JSON files
- **Whapi Ready** - Works with Whapi.cloud webhooks
- **Full Logging** - Detailed logs for debugging webhook and model calls
- **Auto-Fallback** - Tries all API keys × all models before giving up

## Quick Start
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up your Gemini API key(s) - You can use multiple keys for seamless fallback
# Single key:
echo "GEMINI_API_KEY=your_key_here" > .env

# Multiple keys (recommended - comma separated):
echo "GEMINI_API_KEY=key1,key2,key3" > .env

# 3. Start the bot
./restart.sh

# 4. Test it
./test_bot.sh
```

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
{"phone_number": "+1234567890", "message": "Mambo vipi?"}
```

**Whapi format:**
```json
{"from": "+1234567890", "text": "Mambo vipi?"}
```

### `POST /clear/<phone_number>`
Clear conversation history for a user.

## Persona
- Cleven's personal AI
- Concise, polished, playful tone
- Light Kiswahili slang ("mimi nachoka", "ntakulokotea mawe")
- Deflects relationship advice with humor
- Says "God" when asked who created it

## Documentation
See [docs/USAGE.md](docs/USAGE.md) for:
- Whapi integration steps
- Testing locally
- Log monitoring
- Memory behavior details

## License
See [LICENSE](LICENSE)
