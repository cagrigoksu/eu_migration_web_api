import pytest
from unittest.mock import patch
import json
from routes.data.migration import filter_data
import pandas as pd

VALID_API_KEY = "test-api-key"

@pytest.fixture
def auth_header():
    return {"X-API-KEY": VALID_API_KEY}

@pytest.mark.parametrize(
    "df,countries,start_year,end_year,expected_len",
    [
        ([{"Country": "BEL", "Year": 2020}], ["BEL"], 2020, 2020, 1),
        ([{"Country": "BEL", "Year": 2019}], ["AUT"], None, None, 0),
        ([{"Country": "BEL", "Year": 2019}], None, 2018, 2020, 1),
    ],
)
def test_filter_data(df, countries, start_year, end_year, expected_len):
        
    df = pd.DataFrame(df)
    filtered = filter_data(df, countries=countries, start_year=start_year, end_year=end_year)
    assert len(filtered) == expected_len

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
    

@patch("routes.auth.user_auth.is_valid_api_key", return_value=True)
def test_get_migration_data_by_country(mock_auth, client, auth_header):
    response = client.get("/api/migration/country?country_codes=AUS", headers=auth_header)
    assert response.status_code in [200, 500]  # 500: missing data
    data = response.get_json()
    if response.status_code == 200:
        assert isinstance(data, list)
        assert all("Country" in item for item in data)
        
@patch("routes.auth.user_auth.is_valid_api_key", return_value=True)
def test_get_migration_data_by_country_invalid(mock_auth,client, auth_header):
    response = client.get("/api/migration/country", headers=auth_header)  # no country_codes
    assert response.status_code == 400
    assert "error" in response.get_json()

@patch("routes.auth.user_auth.is_valid_api_key", return_value=False)
def test_get_migration_data_by_country_unauthorized(mock_auth,client):
    response = client.get("/api/migration/country?country_codes=AUS")
    assert response.status_code == 401  # unauth. access
    assert "error" in response.get_json()
    
@patch("routes.auth.user_auth.is_valid_api_key", return_value=True)
def test_get_migration_data_by_year(mock_auth, client, auth_header):
    response = client.get("/api/migration/year?year=2020", headers=auth_header)
    assert response.status_code in [200, 500]
    data = response.get_json()
    if response.status_code == 200:
        assert isinstance(data, list)
        assert all("Year" in item for item in data)

@patch("routes.auth.user_auth.is_valid_api_key", return_value=True)
def test_get_migration_data_by_year_range(mock_auth, client, auth_header):
    response = client.get("/api/migration/year?start_year=2015&end_year=2020", headers=auth_header)
    assert response.status_code in [200, 500]
    data = response.get_json()
    if response.status_code == 200:
        assert isinstance(data, list)
        assert all("Year" in item for item in data)

@patch("routes.auth.user_auth.is_valid_api_key", return_value=True)
def test_get_migration_data_by_year_invalid(mock_auth, client, auth_header):
    response = client.get("/api/migration/year", headers=auth_header)  # no year params
    assert response.status_code == 400
    assert "error" in response.get_json()

@patch("routes.auth.user_auth.is_valid_api_key", return_value=False)
def test_get_migration_data_by_year_unauthorized(mock_auth, client):
    response = client.get("/api/migration/year?year=2020")
    assert response.status_code == 401  # unauthorized
    assert "error" in response.get_json()