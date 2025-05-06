# File: roteamento_ia_backend/routers/execute.py
from fastapi import APIRouter, HTTPException, Path, Form, File, UploadFile
from typing import Tuple, Optional, Dict, Any
import time, json
import logging

from roteamento_ia_backend.db.schemas import InputPayload, ExecutionIn, ExecutionOut
from roteamento_ia_backend.db.crud import get_prompt_by_id, create_execution
from roteamento_ia_backend.core.openai.openai_service import generate_openai_completion
from roteamento_ia_backend.core.gemini.gemini_service import generate_gemini_completion
from roteamento_ia_backend.utils.file_utils import extract_text_from_pdf, extract_text_from_image, file_to_base64
from roteamento_ia_backend.core.logging import logger

router = APIRouter()

async def _select_model_fn(ia_model: str) -> Tuple:
    """Retorna a função de geração e flag de async com base no modelo."""
    if ia_model.lower().startswith("gpt"):
        return generate_openai_completion, True
    return generate_gemini_completion, False

async def _execute_common(payload: ExecutionIn) -> ExecutionOut:
    """Lógica comum de execução a partir de um ExecutionIn validado."""
    ia_model = payload.ia_model or "gemini-1.5"
    vars_dict = payload.variables

    # Extrai apenas o texto ou conteúdo dos inputs
    user_text = ""
    input_payload = {}
    
    if payload.input:
        input_payload = payload.input.dict()
        # Extrai apenas o texto do input
        user_text = input_payload.get('data', '')
    else:
        input_file = payload.input_file  # garantido pelo model_validator
        mime = input_file.content_type
        if mime == "application/pdf":
            user_text = await extract_text_from_pdf(input_file)
        elif mime.startswith("image/") or mime.startswith("audio/"):
            # Para arquivos binários, mantemos a forma base64 para o modelo processar
            user_text = f"data:{mime};base64," + await file_to_base64(input_file)
        else:
            raw = await input_file.read()
            user_text = raw.decode("utf-8", errors="ignore")
            
        input_payload = {
            "file_name": input_file.filename,
            "mime_type": mime,
            "content": user_text,
        }

    # Busca e renderiza o prompt
    prompt = await get_prompt_by_id(payload.prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt não encontrado")
    
    try:
        rendered = prompt.template.format(**vars_dict)
    except KeyError as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Variável {str(e)} mencionada no template, mas não fornecida nos parâmetros"
        )

    # Seleciona engine de IA
    generate_fn, is_async = await _select_model_fn(ia_model)

    # Executa IA e mede latência - passando apenas o texto do usuário
    start = time.time()
    try:
        logger.info(f"Executando modelo {ia_model} com prompt: {rendered[:100]}...")
        
        if is_async:
            result = await generate_fn(f"{rendered}\n\nUser Input: {user_text}", ia_model)
        else:
            result = generate_fn(f"{rendered}\n\nUser Input: {user_text}", ia_model)
            
        # Converte resultado para formato serializável se necessário
        serializable_result = _ensure_serializable(result)
        logger.info(f"Resposta recebida do modelo {ia_model} com {len(str(serializable_result))} caracteres")
        
    except Exception as e:
        logger.error(f"Erro ao executar modelo {ia_model}: {str(e)}")
        serializable_result = f"Erro ao executar modelo {ia_model}: {str(e)}"
        
    latency_ms = int((time.time() - start) * 1000)
    cost = 0.0

    # Persiste métricas de execução
    try:
        await create_execution({
            "prompt_id": payload.prompt_id,
            "input": input_payload,
            "output": serializable_result,
            "ia_model": ia_model,
            "latency_ms": latency_ms,
            "cost": cost,
        })
    except Exception as e:
        logger.error(f"Erro ao salvar execução no banco de dados: {str(e)}")
        # Não falha a request se não conseguir salvar métricas

    return ExecutionOut(output=serializable_result, latency_ms=latency_ms, cost=cost)

def _ensure_serializable(result: Any) -> Any:
    """
    Certifica que o resultado é serializável para MongoDB.
    Converte objetos complexos (como do Gemini API) para strings.
    """
    # Se for um tipo primitivo serializável, retorna diretamente
    if isinstance(result, (str, int, float, bool, type(None))):
        return result
    
    # Se for lista ou dicionário, tenta converter recursivamente
    if isinstance(result, list):
        return [_ensure_serializable(item) for item in result]
    if isinstance(result, dict):
        return {k: _ensure_serializable(v) for k, v in result.items()}
    
    # Tenta extrair o texto de objetos do Gemini/OpenAI API
    try:
        # Verifica se é um objeto Content do Gemini
        if hasattr(result, 'parts') and len(getattr(result, 'parts', [])) > 0:
            if hasattr(result.parts[0], 'text'):
                return result.parts[0].text
        
        # Verifica outros atributos comuns
        for attr in ['text', 'content', 'message', 'choices']:
            if hasattr(result, attr):
                value = getattr(result, attr)
                
                # Se for 'choices', tenta pegar o content da primeira choice
                if attr == 'choices' and isinstance(value, list) and len(value) > 0:
                    choice = value[0]
                    if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                        return choice.message.content
                        
                # Tenta converter o valor recursivamente
                return _ensure_serializable(value)
        
        # Último recurso: converte para representação de string
        return str(result)
    except Exception as e:
        logger.error(f"Erro ao serializar resultado: {str(e)}")
        # Em caso de erro, retorna uma representação genérica do objeto
        return f"Resposta não serializável: {type(result).__name__}"

@router.post("", response_model=ExecutionOut)
async def execute_default(
    prompt_id: str = Form(...),
    ia_model: str = Form("gemini-1.5"),
    variables: str = Form("{}"),
    input_text: Optional[str] = Form(None),
    input_file: Optional[UploadFile] = File(None),
):
    """
    Executa um prompt de IA (texto ou arquivo) via multipart/form-data.
    """
    try:
        vars_dict = json.loads(variables)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="O campo `variables` deve ser um JSON válido")
    
    payload_data: Dict[str, Any] = {
        "prompt_id": prompt_id,
        "ia_model": ia_model,
        "variables": vars_dict,
    }
    
    if input_text:
        payload_data["input"] = InputPayload(type="text", data=input_text)
    elif input_file:
        payload_data["input_file"] = input_file
    else:
        raise HTTPException(status_code=400, detail="É preciso enviar `input_text` ou um `input_file`")

    payload = ExecutionIn(**payload_data)
    return await _execute_common(payload)

@router.post("/{ia_model}", response_model=ExecutionOut)
async def execute_with_model(
    ia_model: str = Path(..., description="Nome do modelo de IA (ex: gemini-1.5)"),
    prompt_id: str = Form(...),
    variables: str = Form("{}"),
    input_text: Optional[str] = Form(None),
    input_file: Optional[UploadFile] = File(None),
):
    """
    Executa um prompt de IA usando o modelo especificado na URL via multipart/form-data.
    """
    try:
        vars_dict = json.loads(variables)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="O campo `variables` deve ser um JSON válido")
        
    payload_data: Dict[str, Any] = {
        "prompt_id": prompt_id,
        "ia_model": ia_model,
        "variables": vars_dict,
    }
    
    if input_text:
        payload_data["input"] = InputPayload(type="text", data=input_text)
    elif input_file:
        payload_data["input_file"] = input_file
    else:
        raise HTTPException(status_code=400, detail="É preciso enviar `input_text` ou um `input_file`")

    payload = ExecutionIn(**payload_data)
    return await _execute_common(payload)