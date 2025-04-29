from roteamento_ia_backend.core.gemini.gemini_client import GeminiClient

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
    response = client.generate(prompt, model=model)
    return response.text

