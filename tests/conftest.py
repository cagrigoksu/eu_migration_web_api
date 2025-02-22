import pytest
from app import app  

@pytest.fixture
def client():
   
    app.testing = True  # eanble flask testing mode    
    with app.test_client() as client:
        yield client
