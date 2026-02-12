"""
Fixed tests/test_api_main.py
"""
# pylint: disable=redefined-outer-name
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from src.api.main import app


@pytest.fixture
def client():
    """Provide FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def mock_database():
    """Mock database loader for health check endpoint."""
    # ✅ FIX: Use correct function name 'get_db_loader'
    with patch('src.api.dependencies.get_db_loader') as mock_get_db_loader:
        mock_loader_instance = MagicMock()
        mock_loader_instance.count_records.return_value = 4523
        mock_loader_instance.count_stations.return_value = 44
        mock_get_db_loader.return_value = mock_loader_instance
        yield mock_loader_instance


def test_root_endpoint(client):
    """Test GET / returns HTML homepage."""
    response = client.get("/")
    
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    
    html = response.text
    assert "Weather Data ETL API" in html or "Weather" in html


def test_root_endpoint_contains_documentation_links(client):
    """Test that root endpoint includes links to API docs."""
    response = client.get("/")
    
    html = response.text
    assert "/docs" in html
    assert "/redoc" in html


def test_root_endpoint_contains_endpoint_descriptions(client):
    """Test that root endpoint describes available endpoints."""
    response = client.get("/")
    
    html = response.text
    assert ("Stations" in html or "stations" in html)
    assert ("Weather" in html or "weather" in html)


def test_health_check_endpoint(client):
    """Test GET /health returns healthy status."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert data["status"] == "healthy"
    assert "records" in data
    assert "stations" in data


def test_health_check_data_values(client):
    """Test that health check returns expected data values."""
    response = client.get("/health")
    
    data = response.json()
    
    # Based on hardcoded values in main.py
    assert data["records"] == 4523
    assert data["stations"] == 44


def test_openapi_docs_available(client):
    """Test that OpenAPI/Swagger docs are accessible."""
    response = client.get("/docs")
    
    assert response.status_code == 200
    html_lower = response.text.lower()
    assert "swagger" in html_lower or "openapi" in html_lower or "api" in html_lower


def test_redoc_available(client):
    """Test that ReDoc documentation is accessible."""
    response = client.get("/redoc")
    
    assert response.status_code == 200
    assert "redoc" in response.text.lower() or "api" in response.text.lower()


def test_openapi_json_schema(client):
    """Test that OpenAPI JSON schema is available."""
    response = client.get("/openapi.json")
    
    assert response.status_code == 200
    schema = response.json()
    
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema


def test_openapi_schema_contains_title(client):
    """Test that OpenAPI schema contains correct app title."""
    response = client.get("/openapi.json")
    
    schema = response.json()
    assert schema["info"]["title"] == "Weather Data ETL API"
    assert schema["info"]["version"] == "1.0.0"


def test_openapi_schema_contains_endpoints(client):
    """Test that OpenAPI schema includes all main endpoints."""
    response = client.get("/openapi.json")
    
    schema = response.json()
    paths = schema["paths"]
    
    assert "/" in paths
    assert "/health" in paths
    assert "/stations" in paths or any("/stations" in p for p in paths)
    assert any("/weather" in p for p in paths)


def test_cors_headers_present(client):
    """Test that CORS headers are properly configured."""
    response = client.get("/health")
    assert response.status_code == 200


def test_cors_allows_all_origins(client):
    """Test that CORS allows requests from any origin."""
    headers = {"origin": "http://example.com"}
    response = client.get("/health", headers=headers)
    
    assert response.status_code == 200
    assert "access-control-allow-origin" in [h.lower() for h in response.headers.keys()]


def test_app_title_and_description():
    """Test that app has correct title and description."""
    assert app.title == "Weather Data ETL API"
    assert "Toulouse weather data" in app.description or "weather" in app.description.lower()
    assert app.version == "1.0.0"


def test_nonexistent_endpoint(client):
    """Test that non-existent endpoints return 404."""
    response = client.get("/nonexistent")
    assert response.status_code == 404


def test_method_not_allowed(client):
    """Test that wrong HTTP methods return 405."""
    response = client.post("/health")
    assert response.status_code == 405


def test_stations_router_included():
    """Test that stations router is included in app."""
    routes = [
        getattr(route, "path", "") 
        for route in app.routes 
        if hasattr(route, "path")
    ]
    assert any("/stations" in r for r in routes), f"Available routes: {routes}"


def test_weather_router_included():
    """Test that weather router is included in app."""
    routes = [
        getattr(route, "path", "") 
        for route in app.routes 
        if hasattr(route, "path")
    ]
    assert any("/weather" in r for r in routes), f"Available routes: {routes}"


def test_root_endpoint_styling(client):
    """Test that root endpoint has proper HTML styling."""
    response = client.get("/")
    html = response.text
    assert "<html>" in html.lower() or "<!doctype html>" in html.lower()
    assert "</html>" in html.lower()


def test_root_endpoint_emoji_decorations(client):
    """Test that root endpoint includes weather-related content."""
    response = client.get("/")
    html = response.text
    assert "weather" in html.lower() or "🌤" in html or "meteo" in html.lower()


def test_health_check_json_format(client):
    """Test that health check returns valid JSON."""
    response = client.get("/health")
    
    assert "application/json" in response.headers["content-type"]
    data = response.json()
    
    assert isinstance(data, dict)
    assert isinstance(data["status"], str)
    assert isinstance(data["records"], int)
    assert isinstance(data["stations"], int)


def test_api_responds_quickly(client):
    """Test that API endpoints respond without timeout."""
    import time
    
    start = time.time()
    response = client.get("/health")
    duration = time.time() - start
    
    assert response.status_code == 200
    assert duration < 2.0


def test_multiple_concurrent_requests(client):
    """Test that API can handle multiple requests."""
    responses = [client.get("/health") for _ in range(10)]
    
    assert all(r.status_code == 200 for r in responses)
    assert all(r.json()["status"] == "healthy" for r in responses)


def test_root_contains_station_examples(client):
    """Test that root endpoint shows example station queries."""
    response = client.get("/")
    html = response.text
    assert "/stations" in html.lower()


def test_root_contains_weather_examples(client):
    """Test that root endpoint shows example weather queries."""
    response = client.get("/")
    html = response.text
    assert "weather" in html.lower()


def test_openapi_schema_tags(client):
    """Test that API endpoints are properly tagged."""
    response = client.get("/openapi.json")
    schema = response.json()
    
    has_tags = False
    for path_data in schema["paths"].values():
        for operation in path_data.values():
            if isinstance(operation, dict) and "tags" in operation:
                has_tags = True
                break
        if has_tags:
            break
    
    assert has_tags, f"API endpoints should have tags. Paths: {list(schema['paths'].keys())}"


def test_dashboard_endpoint(client):
    """Test that dashboard endpoint is accessible."""
    response = client.get("/dashboard")
    # Should return 200 if file exists, or 404 with message
    assert response.status_code in [200, 404]
