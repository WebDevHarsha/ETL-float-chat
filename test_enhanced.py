"""
Test script for the enhanced ETL FloatChat with LangChain and LangGraph
"""
import requests
import json
import time

# API endpoint
BASE_URL = "http://localhost:5001"

def test_health():
    """Test the health endpoint"""
    print("🏥 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_schema():
    """Test the schema endpoint"""
    print("📋 Testing schema endpoint...")
    response = requests.get(f"{BASE_URL}/schema")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_query(query):
    """Test a natural language query"""
    print(f"🔍 Testing query: '{query}'")
    
    payload = {"query": query}
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/query", json=payload)
    request_time = time.time() - start_time
    
    print(f"Status: {response.status_code}")
    print(f"Request time: {request_time:.3f}s")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Success!")
        print(f"SQL Generated: {result.get('sql_query')}")
        print(f"Results count: {result.get('row_count')}")
        print(f"Execution time: {result.get('execution_time')}s")
        print(f"Total processing time: {result.get('total_processing_time')}s")
        print(f"Workflow state: {result.get('workflow_state')}")
    else:
        print("❌ Error!")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    print("-" * 50)
    print()

def test_invalid_query():
    """Test invalid query validation"""
    print("🚫 Testing invalid query validation...")
    
    # Test empty query
    response = requests.post(f"{BASE_URL}/query", json={})
    print(f"Empty query status: {response.status_code}")
    
    # Test malicious query
    malicious_query = "DROP TABLE ocean_data; SELECT * FROM users;"
    response = requests.post(f"{BASE_URL}/query", json={"query": malicious_query})
    print(f"Malicious query status: {response.status_code}")
    if response.status_code != 200:
        print(f"Response: {response.json()}")
    
    print()

def main():
    """Run all tests"""
    print("🧪 Starting ETL FloatChat Enhanced Tests\n")
    
    # Test endpoints
    test_health()
    test_schema()
    
    # Test sample queries
    sample_queries = [
        "Show me temperature and salinity data for depths greater than 100m",
        "What is the average oxygen level at different stations?",
        "Find locations with high fluorescence values",
        "Show temperature data for cruise 1",
        "What's the maximum depth recorded?"
    ]
    
    for query in sample_queries:
        test_query(query)
    
    # Test validation
    test_invalid_query()
    
    print("🎉 All tests completed!")

if __name__ == "__main__":
    main()