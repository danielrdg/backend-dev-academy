from bson import ObjectId
from pydantic import BaseModel, Field
from typing import List, Any

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

class PromptModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    template: str
    ia_model: str
    variables: List[str] = []

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

class ExecutionModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    prompt_id: str
    input: Any
    output: Any
    ia_model: str
    latency_ms: int
    cost: float

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
