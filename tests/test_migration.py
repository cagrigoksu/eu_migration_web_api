import pytest
from unittest.mock import patch
import json

VALID_API_KEY = "test-api-key"

@pytest.fixture
def auth_header():
    return {"X-API-KEY": VALID_API_KEY}

@patch("routes.auth.user_auth.is_valid_api_key", return_value=True)
def test_get_migration_data(mock_auth, client, auth_header):

    response = client.get("/api/migration/migration_data", headers=auth_header)

    assert response.status_code == 200
    data = response.get_json()
    
    assert isinstance(data, list)  # is a list of migration records
    if data:  # check its structure
        assert "Country" in data[0]
        assert "Im_Value" in data[0]
        assert "Em_Value" in data[0]
        assert "Net_Migration" in data[0]
        assert "Year" in data[0]

@patch("routes.auth.user_auth.is_valid_api_key", return_value=False)
def test_get_migration_data_unauthorized(mock_auth, client):
    response = client.get("/api/migration/migration_data")
    
    assert response.status_code == 401  # unauthorized access
    assert "error" in response.get_json()
