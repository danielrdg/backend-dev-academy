import os
from dotenv import load_dotenv
import openai

load_dotenv()  
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:  
    raise RuntimeError("OPENAI_API_KEY não definida em .env")

client = openai.ChatCompletion
if not client:  
    raise RuntimeError("Falha ao criar o cliente ChatCompletion")