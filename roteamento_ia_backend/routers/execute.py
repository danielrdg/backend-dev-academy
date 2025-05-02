from fastapi import APIRouter, HTTPException, Form, File, UploadFile
import time, json

from roteamento_ia_backend.db.schemas import ExecutionOut
from roteamento_ia_backend.db.crud import get_prompt_by_id, create_execution
from roteamento_ia_backend.core.openai.openai_service import generate_openai_completion
from roteamento_ia_backend.core.gemini.gemini_service import generate_gemini_completion
from roteamento_ia_backend.utils.file_utils import extract_text_from_pdf, file_to_base64

router = APIRouter()

async def _parse_input(input_text: str, input_file: UploadFile):
    """
    Gera payload de input a partir de texto ou arquivo.
    """
    if input_file:
        mime = input_file.content_type
        if mime == "application/pdf":
            content = await extract_text_from_pdf(input_file)
        elif mime.startswith("image/") or mime.startswith("audio/"):
            content = f"data:{mime};base64," + await file_to_base64(input_file)
        else:
            content = (await input_file.read()).decode("utf-8", errors="ignore")
        return {"file_name": input_file.filename, "mime_type": mime, "content": content}
    elif input_text:
        return {"text": input_text}
    else:
        raise HTTPException(400, "É preciso enviar `input_text` ou um `input_file`")

async def _execute_prompt(
    prompt_id: str,
    ia_model: str,
    vars_dict: dict,
    input_payload: dict,
    generate_fn,
    is_async: bool = True,
):
    # Busca e formata prompt
    prompt = await get_prompt_by_id(prompt_id)
    if not prompt:
        raise HTTPException(404, "Prompt não encontrado")
    rendered = prompt.template.format(**vars_dict)

    # Executa IA
    start = time.time()
    if is_async:
        result = await generate_fn(f"{rendered}\n\nUser Input:\n{input_payload}", ia_model)
    else:
        result = generate_fn(f"{rendered}\n\nUser Input:\n{input_payload}", ia_model)
    latency = int((time.time() - start) * 1000)
    cost = 0.0

    # Persiste
    await create_execution({
        "prompt_id": prompt_id,
        "input": input_payload,
        "output": result,
        "ia_model": ia_model,
        "latency_ms": latency,
        "cost": cost,
    })
    return ExecutionOut(output=result, latency_ms=latency, cost=cost)

@router.post("/openai", response_model=ExecutionOut)
async def execute_openai(
    prompt_id: str         = Form(...),
    ia_model: str          = Form(...),
    variables: str         = Form("{}"),
    input_text: str        = Form(None),
    input_file: UploadFile = File(None),
):
    """Executa o prompt via OpenAI ChatGPT"""
    try:
        vars_dict = json.loads(variables)
    except json.JSONDecodeError:
        raise HTTPException(400, "O campo `variables` deve ser um JSON válido")
    input_payload = await _parse_input(input_text, input_file)
    return await _execute_prompt(
        prompt_id, ia_model, vars_dict, input_payload, generate_openai_completion, True
    )

@router.post("/gemini", response_model=ExecutionOut)
async def execute_gemini(
    prompt_id: str         = Form(...),
    ia_model: str          = Form(...),
    variables: str         = Form("{}"),
    input_text: str        = Form(None),
    input_file: UploadFile = File(None),
):
    """Executa o prompt via Google Gemini"""
    try:
        vars_dict = json.loads(variables)
    except json.JSONDecodeError:
        raise HTTPException(400, "O campo `variables` deve ser um JSON válido")
    input_payload = await _parse_input(input_text, input_file)
    return await _execute_prompt(
        prompt_id, ia_model, vars_dict, input_payload, generate_gemini_completion, False
    )
