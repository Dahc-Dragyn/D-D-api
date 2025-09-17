import pytest
from fastapi.testclient import TestClient

# Import the 'app' object from your main application file
# Make sure main.py is in the same directory or Python path can find it
from main import app

# Create a TestClient instance using your FastAPI app
client = TestClient(app)

# Test function names MUST start with 'test_'
def test_health_check():
    """
    Tests the /health endpoint.
    """
    response = client.get("/health")
    # Assert that the HTTP status code is 200 (OK)
    assert response.status_code == 200
    # Assert that the response body contains the expected JSON
    response_data = response.json()
    assert response_data["status"] == "ok"
    # Check if index_size is present and is an integer (optional but good)
    assert "index_size" in response_data
    assert isinstance(response_data["index_size"], int)
    assert response_data["index_size"] > 0 # Should have loaded docs

def test_query_success_basic():
    """
    Tests a successful query to the /query endpoint.
    """
    query_data = {"query": "goblin", "top_k": 3}
    response = client.post("/query", json=query_data)

    # Assert successful status code
    assert response.status_code == 200
    # Assert the response is valid JSON
    response_data = response.json()
    # Assert the top-level structure is correct
    assert "results" in response_data
    assert isinstance(response_data["results"], list)
    # Assert the number of results matches top_k
    assert len(response_data["results"]) == query_data["top_k"]
    # Assert each result has the expected keys
    if len(response_data["results"]) > 0:
        first_result = response_data["results"][0]
        assert "page_content" in first_result
        assert "metadata" in first_result
        assert "score" in first_result
        # Basic check if the content seems related (case-insensitive)
        assert "goblin" in first_result["page_content"].lower()

def test_query_validation_error_invalid_topk():
    """
    Tests that the API returns a validation error for out-of-range top_k.
    """
    query_data = {"query": "any query", "top_k": 50} # top_k is limited to max 20
    response = client.post("/query", json=query_data)
    # Assert that the status code is 422 (Unprocessable Entity - FastAPI's validation error)
    assert response.status_code == 422

def test_query_validation_error_missing_query():
    """
    Tests that the API returns a validation error if 'query' field is missing.
    """
    query_data = {"top_k": 3} # Missing the required "query" field
    response = client.post("/query", json=query_data)
    # Assert that the status code is 422
    assert response.status_code == 422

# --- You can add many more tests! ---
# Example: Test specific known items
# def test_query_specific_spell():
#     response = client.post("/query", json={"query": "fireball spell", "top_k": 1})
#     assert response.status_code == 200
#     data = response.json()
#     assert len(data["results"]) == 1
#     assert "fireball" in data["results"][0]["metadata"].get("spell_data", {}).get("Spell Name", "").lower()