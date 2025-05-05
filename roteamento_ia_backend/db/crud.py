from typing import List, Optional
from bson import ObjectId
from bson.errors import InvalidId
from statistics import mean

from roteamento_ia_backend.db.mongo import db
from roteamento_ia_backend.db.models import PromptModel, ExecutionModel


async def create_prompt(data: dict) -> PromptModel:
    res = await db.prompts.insert_one(data)
    doc = await db.prompts.find_one({"_id": res.inserted_id})
    return PromptModel(**doc)


async def get_prompts(limit: int = 100, skip: int = 0) -> List[PromptModel]:
    docs = await db.prompts.find().skip(skip).limit(limit).to_list(length=limit)
    return [PromptModel(**d) for d in docs]


async def get_prompt_by_id(pid: str) -> Optional[PromptModel]:
    try:
        oid = ObjectId(pid)
    except InvalidId:
        return None
    doc = await db.prompts.find_one({"_id": oid})
    return PromptModel(**doc) if doc else None


async def update_prompt(pid: str, data: dict) -> bool:
    try:
        oid = ObjectId(pid)
    except InvalidId:
        return False
    res = await db.prompts.update_one({"_id": oid}, {"$set": data})
    return res.modified_count == 1


async def delete_prompt(pid: str) -> bool:
    try:
        oid = ObjectId(pid)
    except InvalidId:
        return False
    res = await db.prompts.delete_one({"_id": oid})
    return res.deleted_count == 1


async def create_execution(data: dict) -> ExecutionModel:
    res = await db.executions.insert_one(data)
    doc = await db.executions.find_one({"_id": res.inserted_id})
    return ExecutionModel(**doc)


async def get_executions_by_prompt(prompt_id: str) -> List[ExecutionModel]:
    docs = await db.executions.find({"prompt_id": prompt_id}).to_list(length=None)
    return [ExecutionModel(**d) for d in docs]


async def get_prompt_metrics(prompt_id: str) -> Optional[dict]:
    try:
        _ = ObjectId(prompt_id)
    except InvalidId:
        return None
    docs = await db.executions.find({"prompt_id": prompt_id}).to_list(length=None)
    if not docs:
        return None
    latencies = [d.get("latency_ms", 0.0) for d in docs if "latency_ms" in d]
    costs = [d.get("cost", 0.0) for d in docs]
    return {
        "total_executions": len(docs),
        "avg_latency_ms": mean(latencies) if latencies else 0.0,
        "avg_cost": mean(costs) if costs else 0.0,
    }
