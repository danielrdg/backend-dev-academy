from fastapi import APIRouter, HTTPException, Path, Form, File, UploadFile
import time, json

from roteamento_ia_backend.db.schemas import ExecutionOut
from roteamento_ia_backend.db.crud import get_prompt_by_id, create_execution
from roteamento_ia_backend.core.openai.openai_service import generate_openai_completion
from roteamento_ia_backend.core.gemini.gemini_service import generate_gemini_completion
from roteamento_ia_backend.utils.file_utils import extract_text_from_pdf, file_to_base64

router = APIRouter()

async def _parse_input(input_text: str = None, input_file: UploadFile = None) -> dict:
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
    if input_text:
        return {"text": input_text}
    raise HTTPException(status_code=400, detail="É preciso enviar `input_text` ou um `input_file`")

async def _execute_prompt(
    prompt_id: str,
    ia_model: str,
    vars_dict: dict,
    input_payload: dict,
    generate_fn,
    is_async: bool,
) -> ExecutionOut:
    # Busca e formata prompt
    prompt = await get_prompt_by_id(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt não encontrado")
    rendered = prompt.template.format(**vars_dict)

    # Executa IA
    start = time.time()
    if is_async:
        result = await generate_fn(f"{rendered}\n\nUser Input:\n{input_payload}", ia_model)
    else:
        result = generate_fn(f"{rendered}\n\nUser Input:\n{input_payload}", ia_model)
    latency_ms = int((time.time() - start) * 1000)
    cost = 0.0

    # Persiste no banco
    await create_execution({
        "prompt_id": prompt_id,
        "input": input_payload,
        "output": result,
        "ia_model": ia_model,
        "latency_ms": latency_ms,
        "cost": cost,
    })
    return ExecutionOut(output=result, latency_ms=latency_ms, cost=cost)

async def _select_model_fn(ia_model: str):
    """Retorna função de geração e flag de async com base no nome do modelo."""
    if ia_model.lower().startswith("gpt"):
        return generate_openai_completion, True
    return generate_gemini_completion, False

@router.post("", response_model=ExecutionOut)
async def execute_default(
    prompt_id: str = Form(...),
    ia_model: str = Form("gemini-1.5"),
    variables: str = Form("{}"),
    input_text: str = Form(None),
    input_file: UploadFile = File(None),
):
    """
    Executa um prompt de IA. Se ia_model não for enviado, usa 'gemini-1.5'.
    """
    try:
        vars_dict = json.loads(variables)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="O campo `variables` deve ser um JSON válido")
    input_payload = await _parse_input(input_text, input_file)
    generate_fn, is_async = await _select_model_fn(ia_model)
    return await _execute_prompt(prompt_id, ia_model, vars_dict, input_payload, generate_fn, is_async)

@router.post("/{ia_model}", response_model=ExecutionOut)
async def execute_with_model(
    ia_model: str = Path(..., description="Nome do modelo de IA (ex: gemini-1.5)"),
    prompt_id: str = Form(...),
    variables: str = Form("{}"),
    input_text: str = Form(None),
    input_file: UploadFile = File(None),
):
    """
    Executa um prompt de IA usando o modelo especificado na URL.
    """
    try:
        vars_dict = json.loads(variables)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="O campo `variables` deve ser um JSON válido")
    input_payload = await _parse_input(input_text, input_file)
    generate_fn, is_async = await _select_model_fn(ia_model)
    return await _execute_prompt(prompt_id, ia_model, vars_dict, input_payload, generate_fn, is_async)
