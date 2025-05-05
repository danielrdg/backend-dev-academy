from fastapi import APIRouter, Depends
from typing import List, Dict, Any
import os
from roteamento_ia_backend.core.logging import logger

router = APIRouter()

@router.get("/", response_model = List[Dict,[str,Any]])
async def list_models():
    """
    Lista todos os modelos disponíveis no sistema
    """

        models = [
        # OpenAI Models
        {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "provider": "openai"},
        {"id": "gpt-4", "name": "GPT-4", "provider": "openai"},
        
        # Google Gemini Models
        {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash", "provider": "google"},
        {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro", "provider": "google"},
        {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash", "provider": "google"},
    ]

    logger.info(f"Returning {len(models)} available models")
    return models