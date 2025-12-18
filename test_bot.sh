#!/bin/bash
# Quick test script for the WhatsApp bot

echo "Testing WhatsApp Bot..."
echo ""

# Test 1: Simple greeting
echo "Test 1: Sending greeting..."
curl -X POST http://localhost:80/webhook \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+255123456789", "message": "Mambo vipi?"}'

echo -e "\n\n"

# Test 2: Ask follow-up
echo "Test 2: Follow-up question..."
curl -X POST http://localhost:80/webhook \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+255123456789", "message": "Unaweza kunisaidia?"}'

echo -e "\n\n"

# Test 3: Check conversation was saved
echo "Test 3: Checking saved conversation..."
if [ -f "data/conversations/255123456789.json" ]; then
    echo "✓ Conversation file exists"
    cat data/conversations/255123456789.json | python3 -m json.tool
else
    echo "✗ No conversation file found"
fi

echo -e "\n\n"

# Test 4: Clear history
echo "Test 4: Clearing history..."
curl -X POST http://localhost:80/clear/+255123456789

echo -e "\n\nDone!"
