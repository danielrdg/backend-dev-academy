
from bson import ObjectId
from typing import List, Any, Dict

from pydantic import BaseModel, Field
from pydantic_core import core_schema
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        """
        Valida strings e desserializa para ObjectId,
        e serializa de volta para string no JSON.
        """
        def validate(value: Any) -> ObjectId:
            if not ObjectId.is_valid(value):
                raise ValueError(f"Invalid ObjectId: {value}")
            return ObjectId(value)

        return core_schema.no_info_plain_validator_function(
            function=validate,
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler) -> Dict[str, Any]:
        """
        Gera o JSON schema como string, para aparecer corretamente no OpenAPI.
        """
        return handler(core_schema.str_schema())


class PromptModel(BaseModel):
    id: PyObjectId           = Field(default_factory=PyObjectId, alias="_id")
    name: str
    template: str
    ia_model: str
    variables: List[str]     = []

    class Config:
        # Para permitir entrada via "_id" e ainda serializar como "id"
        populate_by_name = True
        # Converte ObjectId → str no JSON de saída
        json_encoders = {ObjectId: str}


class ExecutionModel(BaseModel):
    id: PyObjectId           = Field(default_factory=PyObjectId, alias="_id")
    prompt_id: PyObjectId    = Field(..., alias="prompt_id")
    input: Any
    output: Any
    ia_model: str
    latency_ms: int
    cost: float

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
