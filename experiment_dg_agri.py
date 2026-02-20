import requests
import json
from datetime import datetime

API_URL = "https://ec.europa.eu/agrifood/api/wine/prices"

def test_api():
    # Parameters for Spain, Italy, France for recent years
    params = {
        "memberStateCodes": "ES,IT,FR",
        "years": "2024,2025"
    }
    
    try:
        print(f"Requesting {API_URL} with params: {params}")
        response = requests.get(API_URL, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Records returned: {len(data)}")
        
        if len(data) > 0:
            print("\nSample Record:")
            print(json.dumps(data[0], indent=2))
            
            # Helper to find unique descriptions to identify 'bulk' wine
            descriptions = set(d.get('description') for d in data)
            print("\nUnique Descriptions found:")
            for d in sorted(descriptions):
                print(f"- {d}")
        else:
            print("No data returned.")
            
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
             print(f"Response text: {e.response.text}")

if __name__ == "__main__":
    test_api()
