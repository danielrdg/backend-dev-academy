import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import json
from fastapi import UploadFile, HTTPException
from io import BytesIO

from roteamento_ia_backend.routers.execute import _execute_common, _select_model_fn
from roteamento_ia_backend.db.schemas import ExecutionIn, InputPayload
from roteamento_ia_backend.db.models import PromptModel
from bson import ObjectId


@pytest.fixture
def sample_execution_payload():
    return ExecutionIn(
        prompt_id="6507e86b5a458dd52809d552",
        ia_model="gpt-3.5-turbo",
        variables={"name": "John"},
        input=InputPayload(type="text", data="Hello, world!")
    )

@pytest.fixture
def mock_prompt():
    # Create a PromptModel instance instead of a dict
    return PromptModel(
        _id=ObjectId("6507e86b5a458dd52809d552"),
        name="Test Prompt",
        template="This is a template with {name}",
        ia_model="gpt-3.5-turbo",
        variables=["name"]
    )

@pytest.fixture
def mock_file():
    content = b"This is a test file content"
    file = BytesIO(content)
    
    # Create UploadFile without content_type in constructor
    upload_file = UploadFile(filename="test.txt", file=file)
    # Set content_type as an attribute after creation
    upload_file.content_type = "text/plain"
    
    return upload_file

@pytest.mark.asyncio
async def test_select_model_fn():
    """Test selecting the correct model function based on the model name"""
    # Test OpenAI model selection
    openai_models = ["gpt-3.5-turbo", "gpt-4", "GPT-4"]
    for model in openai_models:
        fn, is_async = await _select_model_fn(model)
        assert fn.__name__ == "generate_openai_completion"
        assert is_async is True
    
    # Test Gemini model selection
    gemini_models = ["gemini-1.5", "gemini-pro", "GEMINI-PRO"]
    for model in gemini_models:
        fn, is_async = await _select_model_fn(model)
        assert fn.__name__ == "generate_gemini_completion"
        assert is_async is False

@pytest.mark.asyncio
async def test_execute_common_with_text_input(sample_execution_payload, mock_prompt):
    """Test executing a prompt with text input"""
    # Patch all required functions and classes
    with patch('roteamento_ia_backend.routers.execute.get_prompt_by_id') as mock_get_prompt, \
         patch('roteamento_ia_backend.routers.execute._select_model_fn') as mock_select_fn, \
         patch('roteamento_ia_backend.core.openai.openai_service.generate_openai_completion') as mock_generate, \
         patch('roteamento_ia_backend.routers.execute.create_execution') as mock_create_execution, \
         patch('roteamento_ia_backend.db.schemas.InputPayload.model_dump') as mock_model_dump:
        
        # Setup mocks
        mock_get_prompt.return_value = mock_prompt
        mock_select_fn.return_value = (mock_generate, True)
        mock_generate.return_value = "This is a mock response from the AI model"
        mock_create_execution.return_value = None
        
        # Mock the model_dump method to fix Pydantic v2 compatibility
        mock_model_dump.return_value = {"type": "text", "data": "Hello, world!"}
        
        # Execute the function
        result = await _execute_common(sample_execution_payload)
        
        # Assertions
        assert result.output == "This is a mock response from the AI model"
        assert isinstance(result.latency_ms, int)
        assert isinstance(result.cost, float)
        
        # Verify calls
        mock_get_prompt.assert_called_once_with(sample_execution_payload.prompt_id)
        mock_select_fn.assert_called_once_with(sample_execution_payload.ia_model)
        # Check that generate was called with the right prompt template
        expected_prompt = f"{mock_prompt.template}\n\nUser Input: {sample_execution_payload.input.data}"
        mock_generate.assert_called_once_with(expected_prompt, sample_execution_payload.ia_model)
        
        # Verify create_execution was called with appropriate arguments
        mock_create_execution.assert_called_once()
        execution_data = mock_create_execution.call_args[0][0]
        assert execution_data["prompt_id"] == sample_execution_payload.prompt_id
        assert execution_data["ia_model"] == sample_execution_payload.ia_model
        assert execution_data["output"] == "This is a mock response from the AI model"
        assert isinstance(execution_data["latency_ms"], int)
        assert execution_data["cost"] == 0.0

@pytest.mark.asyncio
async def test_execute_common_with_file_input(mock_prompt, mock_file):
    """Test executing a prompt with file input"""
    # Create execution payload with file input
    file_payload = ExecutionIn(
        prompt_id="6507e86b5a458dd52809d552",
        ia_model="gemini-pro",
        variables={"name": "John"},
        input_file=mock_file
    )
    
    # Patch all required functions and classes
    with patch('roteamento_ia_backend.routers.execute.get_prompt_by_id') as mock_get_prompt, \
         patch('roteamento_ia_backend.routers.execute._select_model_fn') as mock_select_fn, \
         patch('roteamento_ia_backend.core.gemini.gemini_service.generate_gemini_completion') as mock_generate, \
         patch('roteamento_ia_backend.routers.execute.create_execution') as mock_create_execution, \
         patch('roteamento_ia_backend.utils.file_utils.file_to_base64') as mock_file_to_base64:
        
        # Setup mocks
        mock_get_prompt.return_value = mock_prompt
        mock_select_fn.return_value = (mock_generate, False)
        mock_generate.return_value = "This is a mock response for file input"
        mock_create_execution.return_value = None
        mock_file_to_base64.return_value = "base64content"
        
        # Reset file pointer to beginning
        mock_file.file.seek(0)
        
        # Execute the function
        result = await _execute_common(file_payload)
        
        # Assertions
        assert result.output == "This is a mock response for file input"
        assert isinstance(result.latency_ms, int)
        assert isinstance(result.cost, float)
        
        # Verify correct API calls
        mock_get_prompt.assert_called_once_with(file_payload.prompt_id)
        
        # Verify create_execution was called with appropriate arguments
        mock_create_execution.assert_called_once()
        execution_data = mock_create_execution.call_args[0][0]
        assert execution_data["prompt_id"] == file_payload.prompt_id
        assert execution_data["ia_model"] == file_payload.ia_model
        assert execution_data["output"] == "This is a mock response for file input"

@pytest.mark.asyncio
async def test_execute_common_prompt_not_found():
    """Test executing a prompt that doesn't exist"""
    payload = ExecutionIn(
        prompt_id="nonexistent_id",
        ia_model="gpt-3.5-turbo",
        variables={},
        input=InputPayload(type="text", data="Hello")
    )
    
    with patch('roteamento_ia_backend.routers.execute.get_prompt_by_id') as mock_get_prompt:
        # Setup mock to return None (prompt not found)
        mock_get_prompt.return_value = None
        
        # Execute and check for expected exception
        with pytest.raises(HTTPException) as excinfo:
            await _execute_common(payload)
        
        # Verify exception details
        assert excinfo.value.status_code == 404
        assert "Prompt não encontrado" in str(excinfo.value.detail)

@pytest.mark.asyncio
async def test_execute_common_missing_variable():
    """Test executing a prompt with missing required variable"""
    payload = ExecutionIn(
        prompt_id="6507e86b5a458dd52809d552",
        ia_model="gpt-3.5-turbo",
        variables={},  # Empty variables dict
        input=InputPayload(type="text", data="Hello")
    )
    
    # Use PromptModel instead of dict
    mock_prompt = PromptModel(
        _id=ObjectId("6507e86b5a458dd52809d552"),
        name="Test Prompt",
        template="This is a template with {required_var}",  # Requires a variable
        ia_model="gpt-3.5-turbo",
        variables=["required_var"]
    )
    
    with patch('roteamento_ia_backend.routers.execute.get_prompt_by_id') as mock_get_prompt, \
         patch('roteamento_ia_backend.db.schemas.InputPayload.model_dump') as mock_model_dump:
        # Setup mock to return a prompt that requires variables
        mock_get_prompt.return_value = mock_prompt
        mock_model_dump.return_value = {"type": "text", "data": "Hello"}
        
        # Execute and check for expected exception
        with pytest.raises(HTTPException) as excinfo:
            await _execute_common(payload)
        
        # Verify exception details
        assert excinfo.value.status_code == 400
        assert "Variável" in str(excinfo.value.detail)
        assert "mencionada no template" in str(excinfo.value.detail)

@pytest.mark.asyncio
async def test_execute_common_ai_model_error(sample_execution_payload, mock_prompt):
    """Test handling errors from AI model generation"""
    with patch('roteamento_ia_backend.routers.execute.get_prompt_by_id') as mock_get_prompt, \
         patch('roteamento_ia_backend.routers.execute._select_model_fn') as mock_select_fn, \
         patch('roteamento_ia_backend.core.openai.openai_service.generate_openai_completion') as mock_generate, \
         patch('roteamento_ia_backend.routers.execute.create_execution') as mock_create_execution, \
         patch('roteamento_ia_backend.db.schemas.InputPayload.model_dump') as mock_model_dump:
        
        # Setup mocks
        mock_get_prompt.return_value = mock_prompt
        mock_select_fn.return_value = (mock_generate, True)
        # Simulate an error in the AI model
        mock_generate.side_effect = Exception("API error: rate limit exceeded")
        mock_create_execution.return_value = None
        mock_model_dump.return_value = {"type": "text", "data": "Hello, world!"}
        
        # Execute the function - it should not raise an exception but capture it
        result = await _execute_common(sample_execution_payload)
        
        # Assertions - should have error message in output
        assert "Erro ao executar modelo" in result.output
        assert "API error: rate limit exceeded" in result.output
        assert isinstance(result.latency_ms, int)
        assert result.cost == 0.0
        
        # Verify execution was still recorded
        mock_create_execution.assert_called_once()