# WhatsApp Chatbot (Gemini + Whapi)

## Overview
- Powered by **Gemini 1.5 Flash** (stable, generous free tier)
- Cleven's playful, concise youth tone with Kiswahili flavor
- Conversation memory per phone number; only the last 4 user/assistant turns are kept (system prompt is preserved) to save tokens
- Webhook accepts both simple JSON and common Whapi payload shapes

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env` in the repo root:
   ```bash
   GEMINI_API_KEY=your_gemini_api_key_here
   # Optional, if you will push replies via Whapi
   # WHAPI_TOKEN=your_whapi_token
   # WHAPI_BASE_URL=https://gate.whapi.cloud
   ```
3. Run the app (defaults to port 80):
   ```bash
   python src/main.py
   ```

## Behavior
- Persona: Cleven's personal AI; polished, concise, a bit playful. Can drop light Kiswahili slang and sayings like "mimi nachoka" or "ntakulokotea mawe" when it fits. If asked who created you, answer "God". Dodge relationship/girlfriend topics with humor.
- Memory: only message bodies are stored; trims to the last 4 question/answer pairs per phone number. Sessions expire after 24 hours of inactivity.
- User ID: the phone number/chat ID is the session key.

## API Endpoints

### POST `/webhook`
Send an incoming WhatsApp message and get the AI reply. Payloads accepted:

- Simple shape (good for quick tests):
  ```json
  {"phone_number": "+1234567890", "message": "Habari"}
  ```
- Whapi-style shapes commonly sent to webhooks:
  ```json
  {"from": "+1234567890", "text": "Habari"}
  ```
  or
  ```json
  {"messages": [{"from": "+1234567890", "text": "Habari"}]}
  ```

Response example:
```json
{
  "phone_number": "+1234567890",
  "response": "Niko ready, sema!",
  "status": "success"
}
```

Quick curl (simple shape):
```bash
curl -X POST http://localhost:80/webhook \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890", "message": "Niko aje"}'
```

Quick curl simulating a Whapi webhook:
```bash
curl -X POST http://localhost:80/webhook \
  -H "Content-Type: application/json" \
  -d '{"from": "+1234567890", "text": "Mambo"}'
```

### POST `/clear/<phone_number>`
Clears conversation history for the given phone/chat ID.

```bash
curl -X POST http://localhost:80/clear/+1234567890
```

## Whapi integration (chat mode)
1. Set your Whapi webhook URL to point at `http://<your-host>/webhook`.
2. Health check (from their docs):
   ```bash
   curl -H "Authorization: Bearer $WHAPI_TOKEN" "$WHAPI_BASE_URL/checkHealth"
   ```
3. Sending a text reply via Whapi once you have the AI response:
   ```bash
   curl -X POST "$WHAPI_BASE_URL/messages/text" \
     -H "Authorization: Bearer $WHAPI_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"body": "<ai_response>", "chatId": "+1234567890"}'
   ```
   - For group replies (e.g., your "ICT Group"), use the group chatId provided by Whapi, typically shaped like `12345-67890@g.us`.

## Testing memory locally
```bash
# 1) Teach the bot something
curl -X POST http://localhost:80/webhook \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890", "message": "Jina langu ni Cleven"}'

# 2) Ask about it; the bot remembers within the last 4 turns
curl -X POST http://localhost:80/webhook \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890", "message": "Nimekwambia jina langu?"}'
```

## Storage
- Conversations are persisted to JSON files in `data/conversations/` directory.
- Each phone number gets its own JSON file (e.g., `1234567890.json` for `+1234567890`).
- History survives restarts and is automatically loaded on first access.
- Old sessions (24h+ inactive) are automatically deleted.

## Model Selection & Fallback
The bot uses **gemini-1.5-flash-8b** by default (highest free quota), with automatic fallback to:
1. `gemini-1.5-flash-8b` (smallest, fastest, highest quota)
2. `gemini-1.5-flash` (balanced)
3. `gemini-1.5-pro` (most capable, lower quota)

If one model hits quota limits, it automatically tries the next one.

## Logging
All activity is logged to both console and `logs/webhook.log`:
- **[WEBHOOK]** - HTTP requests, payloads, responses
- **[CHATBOT]** - Model initialization, API calls, responses, fallbacks
- **[MEMORY]** - Conversation loading, saving, trimming, cleanup

Check logs to verify:
```bash
# Watch logs in real-time
tail -f logs/webhook.log

# Check app logs
tail -f logs/app.log

# Check last 50 lines
tail -n 50 logs/webhook.log

# Search for specific phone number
grep "+1234567890" logs/webhook.log
```

## Restarting the Bot
After code changes, restart the Flask app:
```bash
./restart.sh
```
