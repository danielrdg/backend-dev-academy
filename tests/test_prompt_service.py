import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from bson import ObjectId

from roteamento_ia_backend.db.models import PromptModel
from roteamento_ia_backend.db.crud import (
    create_prompt, get_prompts, get_prompt_by_id,
    update_prompt, delete_prompt, get_prompt_metrics
)

@pytest.fixture
def sample_prompt_data():
    return {
        "name": "Test Prompt",
        "template": "This is a test prompt with {variable}",
        "ia_model": "gpt-3.5-turbo",
        "variables": ["variable"]
    }

@pytest.fixture
def sample_prompt_model():
    return PromptModel(
        _id=ObjectId("6507e86b5a458dd52809d552"),
        name="Test Prompt",
        template="This is a test prompt with {variable}",
        ia_model="gpt-3.5-turbo",
        variables=["variable"]
    )

@pytest.mark.asyncio
async def test_create_prompt(sample_prompt_data):
    """Test creating a prompt in the database"""
    with patch('roteamento_ia_backend.db.crud.db') as mock_db:
        # Setup mock response
        mock_insert = AsyncMock()
        mock_find_one = AsyncMock()
        mock_db.prompts.insert_one = mock_insert
        mock_db.prompts.find_one = mock_find_one
        
        # Mock the insert_one result
        inserted_id = ObjectId("6507e86b5a458dd52809d552")
        mock_insert.return_value = MagicMock()
        mock_insert.return_value.inserted_id = inserted_id
        
        # Mock the find_one result
        sample_prompt_with_id = sample_prompt_data.copy()
        sample_prompt_with_id["_id"] = inserted_id
        mock_find_one.return_value = sample_prompt_with_id
        
        # Execute the function being tested
        result = await create_prompt(sample_prompt_data)
        
        # Assertions
        assert isinstance(result, PromptModel)
        assert str(result.id) == "6507e86b5a458dd52809d552"
        assert result.name == sample_prompt_data["name"]
        assert result.template == sample_prompt_data["template"]
        assert result.ia_model == sample_prompt_data["ia_model"]
        assert result.variables == sample_prompt_data["variables"]
        
        # Verify the mock calls
        mock_insert.assert_called_once_with(sample_prompt_data)
        mock_find_one.assert_called_once_with({"_id": inserted_id})

@pytest.mark.asyncio
async def test_get_prompts():
    """Test retrieving all prompts from the database"""
    with patch('roteamento_ia_backend.db.crud.db') as mock_db:
        # Create sample data
        sample_prompts = [
            {
                "_id": ObjectId("6507e86b5a458dd52809d552"),
                "name": "Test Prompt 1",
                "template": "Template 1 with {var1}",
                "ia_model": "gpt-3.5-turbo",
                "variables": ["var1"]
            },
            {
                "_id": ObjectId("6507e86b5a458dd52809d553"),
                "name": "Test Prompt 2",
                "template": "Template 2 with {var2}",
                "ia_model": "gemini-pro",
                "variables": ["var2"]
            }
        ]
        
        # Create a mock cursor that can be used in the method chain
        mock_cursor = MagicMock()
        mock_cursor.skip = MagicMock(return_value=mock_cursor)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        mock_cursor.to_list = AsyncMock(return_value=sample_prompts)
        
        # Setup find to return our cursor
        mock_db.prompts.find = MagicMock(return_value=mock_cursor)
        
        # Execute the function being tested
        result = await get_prompts(limit=100, skip=0)
        
        # Assertions
        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], PromptModel)
        assert str(result[0].id) == "6507e86b5a458dd52809d552"
        assert result[0].name == "Test Prompt 1"
        assert result[1].name == "Test Prompt 2"
        
        # Verify the mock calls
        mock_db.prompts.find.assert_called_once()
        mock_cursor.skip.assert_called_once_with(0)
        mock_cursor.limit.assert_called_once_with(100)
        mock_cursor.to_list.assert_called_once_with(length=100)

@pytest.mark.asyncio
async def test_get_prompt_by_id(sample_prompt_model):
    """Test retrieving a prompt by ID"""
    with patch('roteamento_ia_backend.db.crud.db') as mock_db:
        # Setup mock response
        mock_find_one = AsyncMock()
        mock_db.prompts.find_one = mock_find_one
        
        # Valid ID case
        valid_id = "6507e86b5a458dd52809d552"
        mock_find_one.return_value = {
            "_id": ObjectId(valid_id),
            "name": sample_prompt_model.name,
            "template": sample_prompt_model.template,
            "ia_model": sample_prompt_model.ia_model,
            "variables": sample_prompt_model.variables
        }
        
        # Execute the function with valid ID
        result = await get_prompt_by_id(valid_id)
        
        # Assertions for valid ID
        assert isinstance(result, PromptModel)
        assert str(result.id) == valid_id
        assert result.name == sample_prompt_model.name
        
        # Verify the mock calls
        mock_find_one.assert_called_once_with({"_id": ObjectId(valid_id)})
        
        # Reset the mock for the next test
        mock_find_one.reset_mock()
        
        # Invalid ID case - return None
        mock_find_one.return_value = None
        invalid_id = "invalid_id_format"
        result_invalid = await get_prompt_by_id(invalid_id)
        
        # Assertions for invalid ID
        assert result_invalid is None
        # The find_one shouldn't be called with invalid ID as we catch the InvalidId exception
        mock_find_one.assert_not_called()

@pytest.mark.asyncio
async def test_update_prompt():
    """Test updating a prompt"""
    with patch('roteamento_ia_backend.db.crud.db') as mock_db:
        # Setup mock response
        mock_update_one = AsyncMock()
        mock_db.prompts.update_one = mock_update_one
        
        # Mock successful update
        mock_update_one.return_value = MagicMock()
        mock_update_one.return_value.modified_count = 1
        
        # Execute the function with valid data
        valid_id = "6507e86b5a458dd52809d552"
        update_data = {"name": "Updated Name"}
        result = await update_prompt(valid_id, update_data)
        
        # Assertions
        assert result is True
        mock_update_one.assert_called_once_with(
            {"_id": ObjectId(valid_id)}, 
            {"$set": update_data}
        )
        
        # Reset mock
        mock_update_one.reset_mock()
        
        # Mock failed update (no matching document)
        mock_update_one.return_value.modified_count = 0
        result_not_found = await update_prompt(valid_id, update_data)
        
        # Assertions
        assert result_not_found is False
        
        # Invalid ID case - should return False directly
        invalid_id = "invalid_id_format"
        result_invalid = await update_prompt(invalid_id, update_data)
        
        # Assertions for invalid ID
        assert result_invalid is False
        # No additional calls to update_one with invalid ID
        mock_update_one.assert_called_once()  # Only from the previous test case

@pytest.mark.asyncio
async def test_delete_prompt():
    """Test deleting a prompt"""
    with patch('roteamento_ia_backend.db.crud.db') as mock_db:
        # Setup mock response
        mock_delete_one = AsyncMock()
        mock_db.prompts.delete_one = mock_delete_one
        
        # Mock successful delete
        mock_delete_one.return_value = MagicMock()
        mock_delete_one.return_value.deleted_count = 1
        
        # Execute the function with valid ID
        valid_id = "6507e86b5a458dd52809d552"
        result = await delete_prompt(valid_id)
        
        # Assertions
        assert result is True
        mock_delete_one.assert_called_once_with({"_id": ObjectId(valid_id)})
        
        # Reset mock
        mock_delete_one.reset_mock()
        
        # Mock failed delete (no matching document)
        mock_delete_one.return_value.deleted_count = 0
        result_not_found = await delete_prompt(valid_id)
        
        # Assertions
        assert result_not_found is False
        
        # Invalid ID case
        invalid_id = "invalid_id_format"
        result_invalid = await delete_prompt(invalid_id)
        
        # Assertions for invalid ID
        assert result_invalid is False
        # No additional calls to delete_one with invalid ID
        mock_delete_one.assert_called_once()  # Only from the previous test case

@pytest.mark.asyncio
async def test_get_prompt_metrics():
    """Test getting execution metrics for a prompt"""
    with patch('roteamento_ia_backend.db.crud.db') as mock_db:
        # Setup mock responses
        valid_id = "6507e86b5a458dd52809d552"
        
        # Sample executions data
        sample_executions = [
            {
                "_id": ObjectId("6507e86b5a458dd52809d560"),
                "prompt_id": valid_id,
                "latency_ms": 100,
                "cost": 0.001
            },
            {
                "_id": ObjectId("6507e86b5a458dd52809d561"),
                "prompt_id": valid_id,
                "latency_ms": 200,
                "cost": 0.002
            }
        ]
        
        # Create a mock cursor for find() results
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=sample_executions)
        
        # Make find return the cursor
        mock_db.executions.find = MagicMock(return_value=mock_cursor)
        
        # Execute the function with valid ID
        result = await get_prompt_metrics(valid_id)
        
        # Assertions
        assert isinstance(result, dict)
        assert "total_executions" in result
        assert "avg_latency_ms" in result
        assert "avg_cost" in result
        assert result["total_executions"] == 2
        assert result["avg_latency_ms"] == 150.0  # Average of 100 and 200
        assert result["avg_cost"] == 0.0015  # Average of 0.001 and 0.002
        
        # Verify the mock calls
        mock_db.executions.find.assert_called_once_with({"prompt_id": valid_id})
        mock_cursor.to_list.assert_called_once_with(length=None)
        
        # Reset mocks
        mock_db.executions.find.reset_mock()
        mock_cursor.to_list.reset_mock()
        
        # Test no executions found
        mock_cursor.to_list.return_value = []
        result_empty = await get_prompt_metrics(valid_id)
        
        # Assertions
        assert result_empty is None
        
        # Invalid ID case
        invalid_id = "invalid_id_format"
        result_invalid = await get_prompt_metrics(invalid_id)
        
        # Assertions for invalid ID
        assert result_invalid is None