# File: roteamento_ia_backend/routers/execute.py
from fastapi import APIRouter, HTTPException, Path, Form, File, UploadFile
from typing import Tuple, Optional, Dict, Any
import time, json

from roteamento_ia_backend.db.schemas import InputPayload, ExecutionIn, ExecutionOut
from roteamento_ia_backend.db.crud import get_prompt_by_id, create_execution
from roteamento_ia_backend.core.openai.openai_service import generate_openai_completion
from roteamento_ia_backend.core.gemini.gemini_service import generate_gemini_completion
from roteamento_ia_backend.utils.file_utils import extract_text_from_pdf, extract_text_from_image, file_to_base64

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

    # Monta o payload para envio à IA
    if payload.input:
        input_payload = payload.input.dict()
    else:
        input_file = payload.input_file  # garantido pelo model_validator
        mime = input_file.content_type
        if mime == "application/pdf":
            content = await extract_text_from_pdf(input_file)
        elif mime.startswith("image/") or mime.startswith("audio/"):
            content = f"data:{mime};base64," + await file_to_base64(input_file)
        else:
            raw = await input_file.read()
            content = raw.decode("utf-8", errors="ignore")
        input_payload = {
            "file_name": input_file.filename,
            "mime_type": mime,
            "content": content,
        }

    # Busca e renderiza o prompt
    prompt = await get_prompt_by_id(payload.prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt não encontrado")
    rendered = prompt.template.format(**vars_dict)

    # Seleciona engine de IA
    generate_fn, is_async = await _select_model_fn(ia_model)

    # Executa IA e mede latência
    start = time.time()
    if is_async:
        result = await generate_fn(f"{rendered}\n\nUser Input:\n{input_payload}", ia_model)
    else:
        result = generate_fn(f"{rendered}\n\nUser Input:\n{input_payload}", ia_model)
    latency_ms = int((time.time() - start) * 1000)
    cost = 0.0

    # Persiste métricas de execução
    await create_execution({
        "prompt_id": payload.prompt_id,
        "input": input_payload,
        "output": result,
        "ia_model": ia_model,
        "latency_ms": latency_ms,
        "cost": cost,
    })

    return ExecutionOut(output=result, latency_ms=latency_ms, cost=cost)

@router.post("/execute", response_model=ExecutionOut)
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

@router.post("/execute/{ia_model}", response_model=ExecutionOut)
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
