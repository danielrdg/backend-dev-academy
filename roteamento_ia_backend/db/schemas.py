from typing import List, Any, Dict, Optional
from pydantic import BaseModel, Field
from fastapi import UploadFile

class PromptCreate(BaseModel):
    name: str
    template: str
    ia_model: str
    variables: List[str] = Field(default_factory=list)


class PromptOut(BaseModel):
    id: str
    name: str
    template: str
    ia_model: str
    variables: List[str]


class ExecutionIn(BaseModel):
    prompt_id: str
    input: Dict[str, Any]
    variables: Dict[str, Any] = Field(default_factory=dict)
    ia_model: Optional[str] = None
    input_file: Optional[UploadFile] = None
    input_text: Optional[str] = None


class ExecutionOut(BaseModel):
    output: Any
    latency_ms: int
    cost: float


class PromptMetrics(BaseModel):
    total_executions: int
    avg_latency_ms: float
    avg_cost: float
