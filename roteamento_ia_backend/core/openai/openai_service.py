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
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Você é um assistente útil e conciso."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
        )
        
        # Extrai o texto da resposta
        return response.choices[0].message.content
    except Exception as e:
        print(f"Erro ao chamar OpenAI API: {e}")
        return f"Erro ao gerar resposta: {str(e)}"