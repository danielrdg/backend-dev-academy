from typing import List
from fastapi import APIRouter, HTTPException, status
from roteamento_ia_backend.db.schemas import PromptCreate, PromptOut, PromptMetrics
from roteamento_ia_backend.db.crud import (
    create_prompt, get_prompts, get_prompt_by_id,
    update_prompt, delete_prompt, get_prompt_metrics
)

router = APIRouter()

@router.post("/", response_model=PromptOut, status_code=status.HTTP_201_CREATED)
async def create(p: PromptCreate):
    new = await create_prompt(p.dict())
    return PromptOut(
        id=str(new.id),
        name=new.name,
        template=new.template,
        ia_model=new.ia_model,
        variables=new.variables
    )

@router.get("/", response_model=List[PromptOut])
async def list_all():
    docs = await get_prompts()
    return [
        PromptOut(
            id=str(d.id),
            name=d.name,
            template=d.template,
            ia_model=d.ia_model,
            variables=d.variables
        ) for d in docs
    ]

@router.get("/{prompt_id}", response_model=PromptOut)
async def retrieve(prompt_id: str):
    p = await get_prompt_by_id(prompt_id)
    if not p:
        raise HTTPException(404, "Prompt not found")
    return PromptOut(
        id=str(p.id),
        name=p.name,
        template=p.template,
        ia_model=p.ia_model,
        variables=p.variables
    )

@router.put("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update(prompt_id: str, p: PromptCreate):
    ok = await update_prompt(prompt_id, p.dict())
    if not ok:
        raise HTTPException(404, "Prompt not found")

@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove(prompt_id: str):
    ok = await delete_prompt(prompt_id)
    if not ok:
        raise HTTPException(404, "Prompt not found")

@router.get("/{prompt_id}/metrics", response_model=PromptMetrics)
async def metrics(prompt_id: str):
    m = await get_prompt_metrics(prompt_id)
    if m is None:
        raise HTTPException(404, "Nenhuma execução encontrada para esse prompt")
    return m
