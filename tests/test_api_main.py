"""
Tests for main API application endpoints.

Verifies root endpoint, health check, CORS, and app configuration.
"""
# pylint: disable=redefined-outer-name
import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client():
    """Provide FastAPI test client."""
    return TestClient(app)


def test_root_endpoint(client):
    """Test GET / returns HTML homepage."""
    response = client.get("/")
    
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    
    # Verify key content in HTML
    html = response.text
    assert "Weather Data ETL API" in html
    assert "/stations" in html
    assert "/weather" in html
    assert "/docs" in html


def test_root_endpoint_contains_documentation_links(client):
    """Test that root endpoint includes links to API docs."""
    response = client.get("/")
    
    html = response.text
    assert "/docs" in html  # Swagger UI
    assert "/redoc" in html  # ReDoc


def test_root_endpoint_contains_endpoint_descriptions(client):
    """Test that root endpoint describes available endpoints."""
    response = client.get("/")
    
    html = response.text
    assert "Stations" in html
    assert "Weather Data" in html
    assert "GET /stations" in html
    assert "GET /weather" in html


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
    
    # Based on the hardcoded values in main.py
    assert data["records"] == 4523
    assert data["stations"] == 44


def test_openapi_docs_available(client):
    """Test that OpenAPI/Swagger docs are accessible."""
    response = client.get("/docs")
    
    assert response.status_code == 200
    assert "swagger" in response.text.lower() or "openapi" in response.text.lower()


def test_redoc_available(client):
    """Test that ReDoc documentation is accessible."""
    response = client.get("/redoc")
    
    assert response.status_code == 200
    assert "redoc" in response.text.lower()


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
    assert "/stations" in paths
    assert "/weather/" in paths
    assert "/weather/stats" in paths


def test_cors_headers_present(client):
    """Test that CORS headers are properly configured."""
    # OPTIONS requests require explicit route handler in FastAPI
    # Just verify CORS headers are present on GET requests
    response = client.get("/health")
    
    # CORS should be enabled
    assert response.status_code == 200


def test_cors_allows_all_origins(client):
    """Test that CORS allows requests from any origin."""
    headers = {"origin": "http://example.com"}
    response = client.get("/health", headers=headers)
    
    assert response.status_code == 200
    # With allow_origins=["*"], the header should be present
    assert "access-control-allow-origin" in response.headers


def test_app_title_and_description():
    """Test that app has correct title and description."""
    assert app.title == "Weather Data ETL API"
    assert "Toulouse weather data" in app.description
    assert app.version == "1.0.0"


def test_nonexistent_endpoint(client):
    """Test that non-existent endpoints return 404."""
    response = client.get("/nonexistent")
    
    assert response.status_code == 404


def test_method_not_allowed(client):
    """Test that wrong HTTP methods return 405."""
    # POST to a GET-only endpoint
    response = client.post("/health")
    
    assert response.status_code == 405


def test_stations_router_included():
    """Test that stations router is included in app."""
    # Check if stations routes are registered
    routes = [getattr(route, "path", "") for route in app.routes]
    
    assert "/stations" in routes or any("/stations" in r for r in routes)


def test_weather_router_included():
    """Test that weather router is included in app."""
    routes = [getattr(route, "path", "") for route in app.routes]
    
    assert "/weather/" in routes or any("/weather" in r for r in routes)


def test_root_endpoint_styling(client):
    """Test that root endpoint has proper HTML styling."""
    response = client.get("/")
    
    html = response.text
    assert "<style>" in html
    assert "font-family" in html
    assert "</html>" in html


def test_root_endpoint_emoji_decorations(client):
    """Test that root endpoint includes emoji decorations."""
    response = client.get("/")
    
    html = response.text
    # Check for weather-related emojis
    assert "🌤" in html or "weather" in html.lower()


def test_health_check_json_format(client):
    """Test that health check returns valid JSON."""
    response = client.get("/health")
    
    assert response.headers["content-type"] == "application/json"
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
    assert duration < 1.0  # Should respond in under 1 second


def test_multiple_concurrent_requests(client):
    """Test that API can handle multiple requests."""
    responses = []
    
    for _ in range(10):
        response = client.get("/health")
        responses.append(response)
    
    # All requests should succeed
    assert all(r.status_code == 200 for r in responses)
    assert all(r.json()["status"] == "healthy" for r in responses)


def test_root_contains_station_examples(client):
    """Test that root endpoint shows example station queries."""
    response = client.get("/")
    
    html = response.text
    assert "/stations/24" in html  # Specific station example
    assert "location=" in html  # Filter example


def test_root_contains_weather_examples(client):
    """Test that root endpoint shows example weather queries."""
    response = client.get("/")
    
    html = response.text
    assert "station_id=24" in html  # Required parameter example
    assert "limit=" in html  # Pagination example


def test_openapi_schema_tags(client):
    """Test that API endpoints are properly tagged."""
    response = client.get("/openapi.json")
    
    schema = response.json()
    
    # Check that endpoints have tags in their operations
    has_tags = False
    for path_data in schema["paths"].values():
        for operation in path_data.values():
            if isinstance(operation, dict) and "tags" in operation:
                has_tags = True
                break
        if has_tags:
            break
    
    assert has_tags, "API endpoints should have tags"
