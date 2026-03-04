# src/llm_client.py

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_client = None


def get_client() -> Groq:
    """Retourne le client Groq (singleton)"""
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("❌ GROQ_API_KEY non trouvé dans le fichier .env")
        _client = Groq(api_key=api_key)
    return _client


def call_llm(messages: list, temperature: float = 0.7, model: str = None) -> str:
    """
    Appelle l'API Groq avec les messages fournis.

    Args:
        messages  : liste de dict [{"role": "user/assistant/system", "content": "..."}]
        temperature : créativité du modèle (0 = déterministe, 1 = créatif)
        model     : modèle Groq à utiliser (par défaut : LLM_MODEL dans .env)

    Returns:
        str : texte de réponse du LLM
    """
    if model is None:
        model = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

    client = get_client()

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=1024,
    )

    return response.choices[0].message.content