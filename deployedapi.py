import requests
import json
import time

# --- Configuration ---
# Use the Cloud Run URL you just got
API_BASE_URL = "https://dnd-knowledge-api-z3iigmilpq-uw.a.run.app"
HEALTH_ENDPOINT = f"{API_BASE_URL}/health"
QUERY_ENDPOINT = f"{API_BASE_URL}/query"
REQUEST_TIMEOUT = 45 # Seconds, allow time for potential cold start + query

# --- Test Functions ---

def test_health():
    """Tests the /health endpoint."""
    print("--- Testing /health Endpoint ---")
    try:
        start_time = time.time()
        response = requests.get(HEALTH_ENDPOINT, timeout=REQUEST_TIMEOUT)
        end_time = time.time()
        print(f"Status Code: {response.status_code}")
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        print(f"Response JSON: {response.json()}")
        print(f"Time Taken: {end_time - start_time:.2f} seconds")
    except requests.exceptions.RequestException as e:
        print(f"ERROR calling /health: {e}")
    print("-" * 30)

def test_query(query_text: str, top_k: int = 5):
    """Tests the /query endpoint with a specific query."""
    print(f"--- Testing /query Endpoint ---")
    print(f"Query: '{query_text}', top_k: {top_k}")
    payload = {"query": query_text, "top_k": top_k}
    headers = {"Content-Type": "application/json"}
    try:
        start_time = time.time()
        response = requests.post(QUERY_ENDPOINT, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
        end_time = time.time()
        print(f"Status Code: {response.status_code}")
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # Pretty print the JSON response
        response_data = response.json()
        print("Response JSON:")
        print(json.dumps(response_data, indent=2)) # indent=2 makes it readable

        # Optional: Print basic info from results
        if "results" in response_data and response_data["results"]:
             print("\nTop Result Summary:")
             top_result = response_data["results"][0]
             print(f"  Score: {top_result.get('score', 'N/A'):.4f}")
             print(f"  Source: {top_result.get('metadata', {}).get('source', 'N/A')}")
             print(f"  Content Snippet: {top_result.get('page_content', '')[:150]}...") # Show first 150 chars
        print(f"\nTime Taken: {end_time - start_time:.2f} seconds")

    except requests.exceptions.RequestException as e:
        print(f"ERROR calling /query: {e}")
        # Optionally print response text if available, even on error
        if 'response' in locals() and response is not None:
            print(f"Error Response Text: {response.text}")
    print("-" * 30)

# --- Main Execution ---

if __name__ == "__main__":
    print(f"Starting tests against API: {API_BASE_URL}\n")

    # Run health check first
    test_health()

    # Add a small delay - sometimes helpful after first hit if cold starting
    time.sleep(1)

    # Run some query tests
    test_query("What spells can a Wizard learn at level 5?", top_k=3)
    test_query("Describe a Common, Goblin", top_k=2)
    test_query("What are the available backgrounds in the official 5e sourcebooks?", top_k=1)
    test_query("List the available feats for a Rogue character.", top_k=3)

    print("\nTests finished.")