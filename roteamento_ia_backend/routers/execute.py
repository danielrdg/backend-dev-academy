import time
from fastapi import APIRouter, HTTPException
from roteamento_ia_backend.db.schemas import ExecutionIn, ExecutionOut
from roteamento_ia_backend.db.crud import get_prompt_by_id, create_execution

router = APIRouter()

@router.post("/", response_model=ExecutionOut)
async def execute(payload: ExecutionIn):
    prompt = await get_prompt_by_id(payload.prompt_id)
    if not prompt:
        raise HTTPException(404, "Prompt not found")

    text = prompt.template.format(**payload.variables)
    start = time.time()
    result_text = f"Mock resposta: {text}"
    latency = int((time.time() - start) * 1000)
    cost = 0.0

    await create_execution({
        "prompt_id": payload.prompt_id,
        "input": payload.input,
        "output": result_text,
        "ia_model": payload.ia_model,
        "latency_ms": latency,
        "cost": cost
    })

    return ExecutionOut(output=result_text, latency_ms=latency, cost=cost)
