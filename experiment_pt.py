import requests
import json
from datetime import datetime

API_URL = "https://ec.europa.eu/agrifood/api/wine/prices"

def check_portugal():
    print("Fetching DG AGRI data for Portugal (PT)...")
    current_year = datetime.now().year
    params = {
        "memberStateCodes": "PT",
        "years": f"{current_year},{current_year-1}"
    }
    
    try:
        response = requests.get(API_URL, params=params, timeout=30)
        data = response.json()
        
        print(f"Records found: {len(data)}")
        if len(data) > 0:
            print(f"Raw Data Dump: {json.dumps(data)}")
        
        # Analyze descriptions
        descriptions = {}
        for r in data:
            if isinstance(r, str):
                # Maybe it returned a list of error strings?
                print(f"Unexpected string record: {r}")
                continue
                
            desc = r.get('description')
            if desc not in descriptions:
                descriptions[desc] = 0
            descriptions[desc] += 1
            
        print("\nUnique Descriptions found for Portugal:")
        for d, count in descriptions.items():
            print(f"- {d} ({count} records)")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_portugal()
