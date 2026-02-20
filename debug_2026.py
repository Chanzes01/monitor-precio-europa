
import requests
import json
from datetime import datetime

API_URL = "https://ec.europa.eu/agrifood/api/wine/prices"

def check_2026():
    params = {
        "memberStateCodes": "ES,IT,FR",
        "years": "2025"
    }
    print(f"Fetching 2026 data from {API_URL}...")
    response = requests.get(API_URL, params=params, timeout=60)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return

    data = response.json()
    print(f"Total records for 2026: {len(data)}")
    
    # Print distinct descriptions to see if they match our target
    descriptions = set()
    for record in data:
        desc = record.get('description')
        country = record.get('memberStateCode')
        descriptions.add(f"{country}: {desc}")
        
    print("\nAvailable Descriptions in 2026 data:")
    for d in sorted(descriptions):
        print(d)

    # Also print a few full records
    if data:
        print("\nFirst 3 records:")
        print(json.dumps(data[:3], indent=2))

if __name__ == "__main__":
    check_2026()
