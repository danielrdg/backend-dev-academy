from pydantic import BaseModel
from typing import List, Any, Dict

class PromptCreate(BaseModel):
    name: str
    template: str
    ia_model: str
    variables: List[str] = []

class PromptOut(BaseModel):
    id: str
    name: str
    template: str
    ia_model: str
    variables: List[str]

class ExecutionIn(BaseModel):
    prompt_id: str
    input: Dict[str, Any]
    variables: Dict[str, Any] = {}
    ia_model: str

class ExecutionOut(BaseModel):
    output: Any
    latency_ms: int
    cost: float

class PromptMetrics(BaseModel):
    total_executions: int
    avg_latency_ms: float
    avg_cost: float
