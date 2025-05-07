from typing import List, Any, Dict, Optional, Union
from pydantic import BaseModel, Field, model_validator
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


class InputPayload(BaseModel):
    """
    Model for input data with different types.
    
    Attributes:
        type: The type of input ("text", "image", etc.)
        data: The actual input data
    """
    type: str
    data: Any


class FileInputMetadata(BaseModel):
    """
    Model for storing metadata about file inputs.
    
    Attributes:
        file_name: Original file name
        mime_type: MIME type of the file
        content_type: How the content was processed (text/image)
        processing_method: Method used to extract content (OCR, direct read, etc.)
    """
    file_name: str
    mime_type: str
    content_type: str  # "text" or "image"
    processing_method: Optional[str] = None


class ExecutionIn(BaseModel):
    """
    Model for execution request.
    
    Either input or input_file must be provided, but not both.
    """
    prompt_id: str
    ia_model: Optional[str] = None
    variables: Dict[str, Any] = Field(default_factory=dict)

    input: Optional[InputPayload] = None
    input_file: Optional[UploadFile] = None

    @model_validator(mode="after")
    def check_either_input_or_file(cls, m):
        has_input = m.input is not None  
        has_file = m.input_file is not None  
        if has_input == has_file:
            raise ValueError("Provide exactly one of 'input' or 'input_file'")
        return m


class ExecutionOut(BaseModel):
    """
    Model for execution response.
    """
    output: Any
    latency_ms: int
    cost: float


class ExecutionMetadata(BaseModel):
    """
    Extended metadata for execution tracking.
    """
    prompt_id: str
    ia_model: str
    input_type: str  # "text", "image", "pdf", etc.
    total_tokens: Optional[int] = None
    file_metadata: Optional[FileInputMetadata] = None
    execution_time: int  # in milliseconds
    cost: float
    created_at: str


class PromptMetrics(BaseModel):
    total_executions: int
    avg_latency_ms: float
    avg_cost: float
    execution_types: Optional[Dict[str, int]] = None  # Count by input type