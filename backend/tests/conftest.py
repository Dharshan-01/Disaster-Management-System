import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from app.database import create_tables


@pytest.fixture(autouse=True, scope="session")
def init_db():
    """Create all database tables before any tests run."""
    create_tables()
