import pytest
from app.db import init_agent_db
from app.lab_db import init_domain_db,seed_domain

@pytest.fixture(autouse=True)
def setup_db():
    init_agent_db()
    init_domain_db()
    seed_domain()
