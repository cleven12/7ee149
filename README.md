# Cleven's WhatsApp AI Bot

Personal AI assistant for WhatsApp, powered by Google Gemini. Responds with Cleven's playful, youth-gen Kiswahili-flavored style.

## Features
- **Free Gemini Models** - Uses gemini-1.5-flash-8b (highest free quota) with auto-fallback
- **Smart Memory** - Remembers last 4 conversation turns per user
- **Persistent** - Conversation history saved to JSON files
- **Whapi Ready** - Works with Whapi.cloud webhooks
- **Full Logging** - Detailed logs for debugging webhook and model calls
- **Auto-Fallback** - Switches models automatically on quota errors

## Quick Start
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up your Gemini API key
echo "GEMINI_API_KEY=your_key_here" > .env

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
