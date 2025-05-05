import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Set test environment variables
os.environ["MONGO_DB"] = "roteamento_ia_test"
os.environ["MONGO_URI"] = "mongodb://localhost:27017"

from roteamento_ia_backend.main import app

@pytest.fixture(scope="session")
def client():
    return TestClient(app)