from typing import List, Optional
from bson import ObjectId
from roteamento_ia_backend.db.mongo import db
from roteamento_ia_backend.db.models import PromptModel, ExecutionModel
from statistics import mean

async def create_prompt(data: dict) -> PromptModel:
    res = await db.prompts.insert_one(data)
    doc = await db.prompts.find_one({"_id": res.inserted_id})
    return PromptModel(**doc)

async def get_prompts() -> List[PromptModel]:
    docs = await db.prompts.find().to_list(length=100)
    return [PromptModel(**d) for d in docs]

async def get_prompt_by_id(pid: str) -> Optional[PromptModel]:
    doc = await db.prompts.find_one({"_id": ObjectId(pid)})
    return PromptModel(**doc) if doc else None

async def update_prompt(pid: str, data: dict) -> bool:
    res = await db.prompts.update_one({"_id": ObjectId(pid)}, {"$set": data})
    return res.modified_count == 1

async def delete_prompt(pid: str) -> bool:
    res = await db.prompts.delete_one({"_id": ObjectId(pid)})
    return res.deleted_count == 1

async def create_execution(data: dict) -> ExecutionModel:
    res = await db.executions.insert_one(data)
    doc = await db.executions.find_one({"_id": res.inserted_id})
    return ExecutionModel(**doc)

async def get_prompt_metrics(prompt_id: str) -> Optional[dict]:
    docs = await db.executions.find({"prompt_id": prompt_id}).to_list(length=None)
    if not docs:
        return None
    latencies = [d["latency_ms"] for d in docs]
    costs     = [d.get("cost", 0.0) for d in docs]
    return {
        "total_executions": len(docs),
        "avg_latency_ms":   mean(latencies),
        "avg_cost":         mean(costs),
    }
