import openai
import os
from dotenv import load_dotenv


load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env
openai.api_key = os.getenv("OPENAI_API_KEY")    
if not openai.api_key:  # Verifica se a chave da API está definida
    raise RuntimeError("OPENAI_API_KEY não definida em .env")


async def generate_openai_completion(prompt: str, model: str = "gpt-3.5-turbo") -> str:
    resp = await openai.ChatCompletion.acreate(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content
