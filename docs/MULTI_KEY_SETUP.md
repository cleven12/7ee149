# Multiple Gemini API Keys Setup

This guide shows how to configure multiple Gemini API keys for seamless fallback when quotas are exhausted.

## Why Multiple Keys?

Google's free tier has quota limits:
- **Per-minute limits**: 15 requests/minute per model
- **Per-day limits**: 1500 requests/day per model

With multiple keys, the bot automatically switches to another key when one runs out of quota, ensuring **zero downtime**.

## How to Get Multiple API Keys

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create API key #1 (you can use your main Google account)
3. Sign in with a different Google account (Gmail, workspace, etc.)
4. Create API key #2
5. Repeat for as many keys as you need

**Tip**: You can use personal Gmail, school/work accounts, family accounts, etc.

## Configuration

### Option 1: Single API Key (Basic)
```bash
GEMINI_API_KEY=AIzaSy...your_single_key_here
```

### Option 2: Multiple API Keys (Recommended)
```bash
# Comma-separated, no spaces
GEMINI_API_KEY=AIzaSy...key1,AIzaSy...key2,AIzaSy...key3
```

### Option 3: Multiple Keys with Spaces (Also works)
```bash
# Spaces are automatically trimmed
GEMINI_API_KEY=AIzaSy...key1, AIzaSy...key2, AIzaSy...key3
```

## How It Works

### Fallback Logic

For each API key, the bot tries models in this order:
1. `gemini-2.0-flash` (fastest, newest)
2. `gemini-2.5-flash` (alternative flash)
3. `gemini-1.5-flash` (stable, high quota)
4. `gemini-1.5-pro` (most capable)

**Total attempts with 3 keys**: 3 keys × 4 models = **12 attempts** before giving up!

### Example Scenario

You have 3 API keys configured:

```
Request 1: Uses Key #1 + gemini-2.0-flash ✅ Success
Request 2: Uses Key #1 + gemini-2.0-flash ✅ Success
...
Request 50: Key #1 quota exhausted
           → Tries Key #1 + gemini-2.5-flash ✅ Success
...
Request 100: All Key #1 models exhausted
            → Switches to Key #2 + gemini-2.0-flash ✅ Success
...
Request 200: All Key #2 models exhausted
            → Switches to Key #3 + gemini-2.0-flash ✅ Success
...
Request 300: All keys exhausted
            → Returns: "Pole sana! Quota ya API keys zote imekwisha. Jaribu baadae."
```

### Auto-Reset

After a successful request with Key #2 or #3, the bot automatically resets to Key #1 for the next request. This ensures even distribution and quota recovery.

## Monitoring

Check which key/model is being used in the logs:

```bash
tail -f logs/webhook.log | grep CHATBOT
```

You'll see entries like:
```
[CHATBOT] Calling Gemini API (key 1/3, model: gemini-2.0-flash, attempt 1/12)
[CHATBOT] Quota exceeded for key 1 with model gemini-2.0-flash
[CHATBOT] Switched to API key #2
[CHATBOT] Gemini response received (150 chars)
```

## Best Practices

### For Light Usage (< 100 messages/day)
- 1 API key is enough

### For Medium Usage (100-500 messages/day)
- 2-3 API keys recommended

### For Heavy Usage (> 500 messages/day)
- 4+ API keys recommended
- Consider using Google Cloud with billing for unlimited quota

### Quota Reset Times
- **Per-minute quota**: Resets every 60 seconds
- **Per-day quota**: Resets at midnight UTC

## Troubleshooting

### All keys show quota errors immediately
**Cause**: All keys hit their daily limit  
**Solution**: Wait until midnight UTC or add more keys

### Bot keeps using the same key
**Cause**: First key still has quota available  
**Solution**: Normal behavior - it only switches when needed

### "Switched to API key #X" appears in logs constantly
**Cause**: All models on previous keys are exhausted  
**Solution**: Add more API keys or wait for quota reset

### Error: "GEMINI_API_KEY is required"
**Cause**: .env file not loaded or empty  
**Solution**: Check `.env` file exists and has `GEMINI_API_KEY=...`

## Testing Multiple Keys

To test your setup:

```bash
# 1. Add test keys to .env
echo "GEMINI_API_KEY=key1,key2,key3" > .env

# 2. Restart bot
./restart.sh

# 3. Send many messages quickly to trigger quota
# Use the test script:
for i in {1..20}; do
  ./test_bot.sh "Test message $i"
  sleep 1
done

# 4. Watch logs to see key switching
tail -f logs/webhook.log | grep "Switched to API key"
```

## Security Notes

- **Never commit .env file** to Git (already in .gitignore)
- **Keep API keys private** - they provide full access to your Gemini quota
- **Rotate keys regularly** if you suspect they've been exposed
- **Use separate keys** for dev/testing vs production

## Summary

✅ Multiple keys = seamless operation  
✅ Automatic switching when quota exhausted  
✅ Smart model fallback (4 models per key)  
✅ Auto-reset to primary key  
✅ No user-facing errors until all keys exhausted  

With 3 keys, you get **4500 requests/day** (3 × 1500) before hitting limits!
