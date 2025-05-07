from roteamento_ia_backend.core.gemini.gemini_client import GeminiClient
from typing import Optional

def generate_gemini_completion(
        prompt: str,
        model: str = "gemini-2.0-flash",
) -> str:
    """
    Gera uma resposta usando o modelo Gemini.

    Args:
        prompt (str): O prompt a ser enviado para o modelo.
        model (str): O modelo a ser usado. Padrão é "gemini-2.0-flash".

    Returns:
        str: A resposta gerada pelo modelo.
    """
    client = GeminiClient()
    
    # Check if the prompt contains a base64 image
    if "data:image/" in prompt:
        # Extract the parts - text prompt and image
        img_start = prompt.find("data:image/")
        
        # If there's text before the image
        text_prompt = ""
        if img_start > 0:
            text_prompt = prompt[:img_start].strip()
        
        # Extract image data
        img_data = prompt[img_start:]
        
        # Generate with multi-modal content
        return client.generate_multimodal(text_prompt, img_data, model)
    else:
        # Standard text-only completion
        return client.generate(prompt, model=model)