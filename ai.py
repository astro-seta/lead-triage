import os
import json
import time
import httpx
from dotenv import load_dotenv
from google import genai
from google.genai import types, errors

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-3.5-flash-lite"

SYSTEM = """You triage inbound contact-form messages for a law firm.
Return ONLY a JSON object with these keys:
category: one of "new_client", "existing_client", "vendor_spam", "other"
urgency: one of "low", "medium", "high"
summary: one sentence
suggested_reply: a polite reply of 2-3 sentences
No text before or after the JSON."""

RETRY_CODES = (429, 500, 503)   # rate limit or temporary server problems
MAX_ATTEMPTS = 4


def triage(name, email, message):
    for attempt in range(MAX_ATTEMPTS):
        last_try = attempt == MAX_ATTEMPTS - 1
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=f"Name: {name}\nEmail: {email}\nMessage: {message}",
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM,
                    response_mime_type="application/json",
                    max_output_tokens=800,
                ),
            )
            break
        except errors.APIError as e:
            # Google says "busy" or "too many requests": wait and try again
            if e.code in RETRY_CODES and not last_try:
                time.sleep(2 * (attempt + 1))
                continue
            raise
        except (httpx.TransportError, ConnectionError):
            # The internet connection dropped: wait and try again
            if not last_try:
                time.sleep(2 * (attempt + 1))
                continue
            raise

    data = json.loads(response.text)
    usage = response.usage_metadata
    tokens_in = usage.prompt_token_count or 0
    tokens_out = usage.candidates_token_count or 0
    return data, tokens_in, tokens_out