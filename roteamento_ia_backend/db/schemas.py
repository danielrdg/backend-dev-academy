from typing import List, Any, Dict, Optional
from pydantic import BaseModel, Field, root_validator
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
    ia_model: Optional[str] = None
    variables: Dict[str, Any] = Field(default_factory=dict)

    input: Optional[InputPayload] = None
    input_file: Optional[UploadFile] = None

    @root_validator
    def check_either_input_or_file(cls, values):
        has_input = values.get("input") is not None
        has_file = values.get("input_file") is not None
        if has_input == has_file:
            raise ValueError("Informe exatamente um dos campos: 'input' ou 'input_file'.")
        return values



class ExecutionOut(BaseModel):
    output: Any
    latency_ms: int
    cost: float


class PromptMetrics(BaseModel):
    total_executions: int
    avg_latency_ms: float
    avg_cost: float

class InputPayload(BaseModel):
    type: str
    data: Any

