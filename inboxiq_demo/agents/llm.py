"""Single point of LLM access. Swap Groq for Azure OpenAI in production."""
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_client = None
MODEL = "llama-3.3-70b-versatile"  # Free, GPT-4o-class quality on Groq

def get_client():
    global _client
    if _client is None:
        key = os.getenv("GROQ_API_KEY")
        if not key or key.startswith("gsk_paste"):
            raise RuntimeError(
                "Missing GROQ_API_KEY. Get a free key at https://console.groq.com "
                "and put it in your .env file."
            )
        _client = Groq(api_key=key)
    return _client

def chat(system: str, user: str, temperature: float = 0.2, max_tokens: int = 600) -> str:
    """One-shot chat completion. Returns the assistant's text."""
    resp = get_client().chat.completions.create(
        model=MODEL,
        temperature=temperature,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return resp.choices[0].message.content.strip()
