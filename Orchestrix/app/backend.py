import os
import re
import time
from collections import defaultdict
from typing import Dict, Any, Optional

import google.generativeai as genai
from dotenv import load_dotenv
from loguru import logger

# ─────────────────────────────────────────────────────────────

# Environment Setup

# ─────────────────────────────────────────────────────────────

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEFAULT_MODEL = "gemini-2.5-flash"
MAX_INPUT_LENGTH = 1200
RATE_LIMIT_RPM = 20

if not GEMINI_API_KEY:
raise RuntimeError("GEMINI_API_KEY missing in .env")

# ─────────────────────────────────────────────────────────────

# Gemini Setup

# ─────────────────────────────────────────────────────────────

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(DEFAULT_MODEL)

# ─────────────────────────────────────────────────────────────

# Logging

# ─────────────────────────────────────────────────────────────

os.makedirs("logs", exist_ok=True)
logger.add("logs/app.log", rotation="10 MB")

# ─────────────────────────────────────────────────────────────

# Rate Limiter

# ─────────────────────────────────────────────────────────────

_rate_store = defaultdict(list)

def is_rate_limited(user_id: str) -> bool:
now = time.time()
window = 60

```
_rate_store[user_id] = [
    t for t in _rate_store[user_id]
    if now - t < window
]

if len(_rate_store[user_id]) >= RATE_LIMIT_RPM:
    return True

_rate_store[user_id].append(now)
return False
```

# ─────────────────────────────────────────────────────────────

# Basic Injection Protection

# ─────────────────────────────────────────────────────────────

INJECTION_PATTERNS = [
r"ignore previous instructions",
r"system prompt",
r"jailbreak",
r"DAN mode",
]

INJECTION_RE = re.compile(
"|".join(INJECTION_PATTERNS),
re.IGNORECASE
)

def sanitize_input(text: str):
cleaned = text[:MAX_INPUT_LENGTH]
flagged = bool(INJECTION_RE.search(cleaned))
return cleaned, flagged

# ─────────────────────────────────────────────────────────────

# Session Memory

# ─────────────────────────────────────────────────────────────

chat_memory = defaultdict(list)

def remember_message(session_id: str, role: str, content: str):
chat_memory[session_id].append({
"role": role,
"content": content
})

```
# Keep last 6 messages only
chat_memory[session_id] = chat_memory[session_id][-6:]
```

# ─────────────────────────────────────────────────────────────

# Local HR Fallback Answers

# ─────────────────────────────────────────────────────────────

def local_answer(text: str, user: str = "Guest") -> Optional[str]:

```
q = text.lower().strip()

greetings = ["hi", "hello", "hey", "good morning"]

if q in greetings:
    return f"Hello {user}! How can I help you today?"

if "leave" in q:
    return f"{user}, your leave balance system is active and available in the dashboard."

if "salary" in q or "pay" in q:
    return f"{user}, payroll details are available in the payroll section."

if "department" in q:
    return f"Department information is available in the employee dashboard."

return None
```

# ─────────────────────────────────────────────────────────────

# Gemini Response

# ─────────────────────────────────────────────────────────────

def generate_ai_response(prompt: str, user: str = "Guest", session_id: str = "default") -> str:

```
```python id="jlwm2k"
def generate_ai_response(prompt: str, user: str = "Guest", session_id: str = "default") -> str:

    try:

        conversation_context = "\n".join(
            [
                f"{msg['role']}: {msg['content']}"
                for msg in chat_memory[session_id]
            ]
        )

        full_prompt = f"""
You are Orchestrix AI HR Assistant.

Current User: {user}

Previous Conversation:
{conversation_context}

Rules:
- Be professional
- Be concise
- Help with HR-related questions
- Keep responses modern and friendly

Current User Question:
{prompt}
"""

        response = model.generate_content(full_prompt)

        if response and hasattr(response, "text"):

            text = response.text.strip()

            if text:
                return text

        return "No response generated."

    except Exception as e:

        logger.error(f"Gemini Error: {e}")

        return "AI assistant temporarily unavailable."
```

# ─────────────────────────────────────────────────────────────

# Main Public Function

# ─────────────────────────────────────────────────────────────

def get_response(
user_input: str,
user: str = "Guest",
session_id: str = "default"
) -> Dict[str, Any]:

```
try:

    # Rate limit
    if is_rate_limited(session_id):
        return {
            "response": "Too many requests. Please wait a moment.",
            "model_used": "none",
            "error": "rate_limited"
        }

    # Sanitize input
    cleaned_input, flagged = sanitize_input(user_input)

    if flagged:
        return {
            "response": "Suspicious prompt detected.",
            "model_used": "none",
            "error": "prompt_injection"
        }

    # Local fast answers
    local_resp = local_answer(cleaned_input, user)

    if local_resp:
        return {
            "response": local_resp,
            "model_used": "local",
            "error": None
        }

    # Save user message
    remember_message(session_id, "user", cleaned_input)

    # Gemini response
    ai_response = generate_ai_response(cleaned_input, user, session_id)

    # Save assistant response
    remember_message(session_id, "assistant", ai_response)

    logger.info(f"Response generated for session={session_id}")

    return {
        "response": ai_response,
        "model_used": "gemini",
        "error": None
    }

except Exception as e:

    logger.error(f"Backend Error: {e}")

    return {
        "response": "System temporarily unavailable.",
        "model_used": "none",
        "error": str(e)
    }
```
