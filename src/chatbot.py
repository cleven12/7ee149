"""
WhatsApp Chatbot with Gemini integration and tight conversation memory.
Maintains conversation history per phone number.
"""

import os
import logging
from typing import List, Dict, Tuple

from google import genai
from conversation_memory import ConversationMemory

logger = logging.getLogger(__name__)


class WhatsAppChatbot:
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize WhatsApp chatbot with Gemini.

        Args:
            api_key: Single Gemini API key or comma-separated keys (defaults to env GEMINI_API_KEY)
            model: Gemini model to use (if None, will try free models in order)
        """
        # FREE TIER MODELS ONLY - No charges will be incurred
        # Google's free tier provides generous quotas for these models
        # Using correct format for google-genai SDK (no 'models/' prefix)
        self.available_models = [
            "gemini-2.0-flash",             # PRIMARY: Latest, fastest
            "gemini-2.5-flash",             # FALLBACK 1: Latest flash
            "gemini-1.5-flash",             # FALLBACK 2: Stable, high quota
            "gemini-1.5-pro",               # FALLBACK 3: Most capable, lower quota
        ]
        
        self.model_name = model or self.available_models[0]
        logger.info(f"[CHATBOT] Initializing chatbot with model: {self.model_name}")
        
        # Support multiple API keys separated by comma
        api_key_input = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key_input:
            logger.error("[CHATBOT] GEMINI_API_KEY not found")
            raise ValueError("GEMINI_API_KEY is required")

        # Parse multiple keys if provided
        self.api_keys = [key.strip() for key in api_key_input.split(',') if key.strip()]
        self.current_key_index = 0
        logger.info(f"[CHATBOT] Loaded {len(self.api_keys)} API key(s)")

        self.client = genai.Client(api_key=self.api_keys[self.current_key_index])
        logger.info("[CHATBOT] Gemini API client configured successfully")

        self.memory = ConversationMemory(max_pairs=4, session_timeout_hours=24)
        logger.info(f"[CHATBOT] Conversation memory initialized (max_pairs=4, timeout=24h)")
        logger.info(f"[CHATBOT] Available fallback models: {', '.join(self.available_models)}")

        # CGM's personal AI voice and guardrails
        self.default_system_message = """
You are CGM, the official AI Assistant for the MWECAU ICT Club specific on project management.

Role:
- Act as a professional ICT Project Manager assistant.
- Represent the MWECAU ICT Club correctly.
- The Project Manager is Cleven, Laureen and Rafael.
- Official reference: https://github.com/mwecauictclub

Tone:
- Clear, simple, and professional.
- Friendly but serious on ICT and leadership topics.

Responsibilities:
- Answer questions related to ICT, software development, web systems,
  networking, cybersecurity, project management, meetings, workshops,
  training, and ICT clubs.
- Give clear, practical, and accurate answers.
- Use the GitHub reference when relevant.
- Avoid random or unclear responses.

Communication:
- Be direct and helpful.
- Provide feedback on ICT projects when asked.
- Say "I don’t know" if information is not certain.

Safety Rules:
- Do not make up information.
- Do not give legal or misleading technical advice.
- Do not share private data beyond the official contact.
- If asked who created you, answer: "God."
- Do not claim to be human.

Focus:
- Stay within ICT Club, technology, leadership, and project topics.
- Politely ignore or redirect out-of-scope questions.
"""


    def _switch_to_next_key(self) -> bool:
        """
        Switch to the next available API key.
        Returns True if switched successfully, False if no more keys available.
        """
        if self.current_key_index < len(self.api_keys) - 1:
            self.current_key_index += 1
            self.client = genai.Client(api_key=self.api_keys[self.current_key_index])
            logger.info(f"[CHATBOT] Switched to API key #{self.current_key_index + 1}")
            return True
        return False

    def _reset_key_index(self):
        """Reset to first API key after successful request."""
        if self.current_key_index != 0:
            self.current_key_index = 0
            self.client = genai.Client(api_key=self.api_keys[self.current_key_index])
            logger.info("[CHATBOT] Reset to primary API key")


    def _build_prompt(self, history: List[Dict]) -> Tuple[str, str]:
        """Convert stored history into Gemini-friendly prompt."""
        system_message = self.default_system_message
        conversation_parts = []

        for msg in history:
            role = msg.get("role")
            content = msg.get("content", "")

            if role == "system":
                system_message = content or system_message
                continue

            prefix = "User: " if role == "user" else "Assistant: "
            conversation_parts.append(f"{prefix}{content}")

        conversation_text = "\n\n".join(conversation_parts)
        return system_message, conversation_text

    def process_message(self, phone_number: str, user_message: str) -> str:
        """
        Process incoming WhatsApp message and generate response.
        
        Args:
            phone_number: User's phone number (e.g., "+1234567890")
            user_message: Message text from user
        
        Returns:
            AI assistant response
        """
        logger.info(f"[CHATBOT] Processing message for {phone_number}")
        history = self.memory.get_history(phone_number)
        logger.debug(f"[CHATBOT] Retrieved history length: {len(history)} messages")

        # Ensure a system message exists per conversation
        if not history:
            logger.info(f"[CHATBOT] New conversation started for {phone_number}")
            self.memory.set_system_message(phone_number, self.default_system_message)
            history = self.memory.get_history(phone_number)

        # Add user message and rebuild trimmed history
        self.memory.add_message(phone_number, "user", user_message)
        history = self.memory.get_history(phone_number)
        logger.info(f"[CHATBOT] User message added. Current history: {len(history)} messages")

        system_message, conversation_text = self._build_prompt(history)
        logger.debug(f"[CHATBOT] Built prompt with conversation context")

        # Try current model, then fallback to others on quota errors
        models_to_try = [self.model_name] + [m for m in self.available_models if m != self.model_name]
        
        for attempt, model in enumerate(models_to_try):
            try:
                logger.info(f"[CHATBOT] Calling Gemini API (model: {model}, attempt {attempt+1}/{len(models_to_try)})")
                
                # Build full prompt with system instruction and conversation
                full_prompt = f"{system_message}\n\n{conversation_text}"
                
                response = self.client.models.generate_content(
                    model=model,
                    contents=full_prompt
                )
                
                assistant_message = response.text or ""
                logger.info(f"[CHATBOT] Gemini response received ({len(assistant_message)} chars)")
                logger.debug(f"[CHATBOT] Response preview: {assistant_message[:100]}...")

                # Update to the working model for next time
                if model != self.model_name:
                    logger.info(f"[CHATBOT] Switching default model from {self.model_name} to {model}")
                    self.model_name = model

                # Persist assistant message for future context
                self.memory.add_message(phone_number, "assistant", assistant_message)
                logger.info(f"[CHATBOT] Assistant message saved to history")

                return assistant_message

            except Exception as e:
                error_str = str(e)
                is_quota_error = "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower()
                is_not_found = "404" in error_str or "NOT_FOUND" in error_str or "not found" in error_str.lower()
                
                # Try next model on quota or 404 errors
                if (is_quota_error or is_not_found) and attempt < len(models_to_try) - 1:
                    if is_quota_error:
                        logger.warning(f"[CHATBOT] Quota exceeded for {model}, trying next model...")
                    else:
                        logger.warning(f"[CHATBOT] Model {model} not found, trying next model...")
                    continue
                else:
                    logger.error(f"[CHATBOT] Error calling Gemini API: {error_str}", exc_info=True)
                    if is_quota_error:
                        return "Samahani, Kunachangamoto ya kimfumo kwa sasa, wasiliana nasi kwa njia mbadala kama zilivyo orodheshwa na viongozi."
                    if is_not_found:
                        return "Samahani, Kunachangamoto ya kimfumo kwa sasa, wasiliana nasi kwa njia mbadala kama zilivyo orodheshwa na viongozi"                    
                    return f"Samahani, kuna hitilafu: {error_str}"
        
        return "Samahani, Kunachangamoto ya kimfumo kwa sasa, wasiliana nasi kwa njia mbadala kama zilivyo orodheshwa na viongozi. Jaribu tena baadae."

    def clear_conversation(self, phone_number: str):
        """Clear conversation history for a phone number"""
        self.memory.clear_history(phone_number)

    def set_custom_system_message(self, phone_number: str, system_message: str):
        """Set a custom system message for a specific user"""
        self.memory.set_system_message(phone_number, system_message)
