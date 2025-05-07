import os
from openai import OpenAI
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Inicializa o cliente OpenAI com a chave da API
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY não definida em .env")

client = OpenAI(api_key=api_key)

async def generate_openai_completion(prompt: str, model: str = "gpt-3.5-turbo") -> str:
    """
    Gera uma resposta usando o modelo OpenAI.

    Args:
        prompt (str): O prompt a ser enviado para o modelo.
        model (str): O modelo a ser usado. Padrão é "gpt-3.5-turbo".

    Returns:
        str: A resposta gerada pelo modelo.
    """
    try:
        # Check if prompt contains an image
        if "data:image/" in prompt:
            # For vision-capable models (e.g., gpt-4-vision)
            if model.lower() in ["gpt-4-vision", "gpt-4-turbo", "gpt-4o"]:
                # Extract parts - text prompt and image
                img_start = prompt.find("data:image/")
                text_prompt = prompt[:img_start].strip() if img_start > 0 else ""
                img_data = prompt[img_start:]
                
                # Create messages with content array
                messages = [
                    {"role": "system", "content": "Você é um assistente útil e conciso."},
                    {"role": "user", "content": [
                        {"type": "text", "text": text_prompt},
                        {"type": "image_url", "image_url": {"url": img_data}}
                    ]}
                ]
                
                response = await client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000,
                )
            else:
                # Fallback for non-vision models
                # Remove the image data and add a note
                img_start = prompt.find("data:image/")
                text_prompt = prompt[:img_start].strip() if img_start > 0 else prompt
                text_prompt += "\n[Note: Image processing is only available with GPT-4-Vision, GPT-4-Turbo, or GPT-4o]"
                
                response = await client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "Você é um assistente útil e conciso."},
                        {"role": "user", "content": text_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1000,
                )
        else:
            # Standard text-only completion
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Você é um assistente útil e conciso."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000,
            )
        
        # Extract the text of the response
        return response.choices[0].message.content
    except Exception as e:
        print(f"Erro ao chamar OpenAI API: {e}")
        return f"Erro ao gerar resposta: {str(e)}"