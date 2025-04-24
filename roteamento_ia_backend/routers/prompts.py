from typing import List
from fastapi import APIRouter, HTTPException, status
from roteamento_ia_backend.db.schemas import PromptCreate, PromptOut
from roteamento_ia_backend.db.crud import (
    create_prompt, get_prompts, get_prompt_by_id,
    update_prompt, delete_prompt
)

router = APIRouter()

@router.post("/", response_model=PromptOut, status_code=status.HTTP_201_CREATED)
async def create(p: PromptCreate):
    new = await create_prompt(p.dict())
    return PromptOut(**new.dict())

@router.get("/", response_model=List[PromptOut])
async def list_all():
    docs = await get_prompts()
    return [PromptOut(**d.dict()) for d in docs]

@router.get("/{prompt_id}", response_model=PromptOut)
async def retrieve(prompt_id: str):
    p = await get_prompt_by_id(prompt_id)
    if not p:
        raise HTTPException(404, "Prompt not found")
    return PromptOut(**p.dict())

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
