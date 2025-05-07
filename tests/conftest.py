import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Set test environment variables
os.environ["MONGO_DB"] = "roteamento_ia_test"
os.environ["MONGO_URI"] = "mongodb://localhost:27017"

# Import app after setting environment variables
from roteamento_ia_backend.main import app

# Note: We'll use pytest-asyncio's built-in event_loop fixture
# instead of defining our own to avoid the deprecation warning

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def mock_mongo_db():
    # Create mock collections
    prompts_collection = MagicMock()
    executions_collection = MagicMock()
    
    # Create mock database
    mock_db = MagicMock()
    mock_db.prompts = prompts_collection
    mock_db.executions = executions_collection
    
    # Setup for prompts collection
    prompts_cursor = MagicMock()
    prompts_cursor.skip = MagicMock(return_value=prompts_cursor)
    prompts_cursor.limit = MagicMock(return_value=prompts_cursor)
    prompts_cursor.to_list = AsyncMock()
    prompts_collection.find = MagicMock(return_value=prompts_cursor)
    prompts_collection.find_one = AsyncMock()
    prompts_collection.insert_one = AsyncMock()
    prompts_collection.update_one = AsyncMock()
    prompts_collection.delete_one = AsyncMock()
    
    # Setup for executions collection
    executions_cursor = MagicMock()
    executions_cursor.to_list = AsyncMock()
    executions_collection.find = MagicMock(return_value=executions_cursor)
    executions_collection.insert_one = AsyncMock()
    
    with patch('roteamento_ia_backend.db.crud.db', mock_db):
        yield mock_db

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client."""
    with patch('roteamento_ia_backend.core.openai.openai_service.client') as mock_client:
        # Mock the chat.completions.create method
        chat_mock = AsyncMock()
        mock_client.chat.completions.create = chat_mock
        
        # Set up a sample response
        response_mock = MagicMock()
        response_mock.choices = [MagicMock()]
        response_mock.choices[0].message.content = "Mocked OpenAI response"
        chat_mock.return_value = response_mock
        
        yield mock_client

@pytest.fixture
def mock_gemini_client():
    """Mock Gemini client."""
    with patch('roteamento_ia_backend.core.gemini.gemini_client.GeminiClient.generate') as mock_generate:
        # Set up a sample response
        mock_generate.return_value = "Mocked Gemini response"
        
        yield mock_generate