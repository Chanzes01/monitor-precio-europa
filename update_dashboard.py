import main
import json
import sys
from io import StringIO

def update_data():
    print("Updating wine market data...")
    
    # Capture stdout to silence prints from main.py during execution if desired, 
    # or just rely on the return value.
    # main.extract_dg_agri returns (json_string, status_code)
    
    # We don't need to capture stdout if we just use the return value.
    # The prints will still show in the console (which is fine), 
    # but we will write the RETURNED json to the file.
    
    try:
        # Fetch DG AGRI
        json_dg, status_dg = main.extract_dg_agri(None)
        data_dg = json.loads(json_dg) if status_dg == 200 else []
        
        # Fetch Eurostat
        results_es, status_es = main.extract_eurostat(None)
        data_es = results_es if status_es == 200 else []
        
        # Combine
        combined_data = data_dg + data_es
        
        if combined_data:
            # Save as JSON (for API/other uses)
            with open('latest_data.json', 'w', encoding='utf-8') as f:
                json.dump(combined_data, f, indent=2)
                
            # Save as JS (for local dashboard to avoid CORS)
            with open('data.js', 'w', encoding='utf-8') as f:
                f.write(f"const WINE_DATA = {json.dumps(combined_data, indent=2)};")
                
            print(f"Success! {len(combined_data)} records saved to 'latest_data.json' and 'data.js' ({len(data_dg)} DG AGRI, {len(data_es)} Eurostat).")
        else:
            print("No data found from any source.")
            
    except Exception as e:
        print(f"Failed to update data: {e}")

if __name__ == "__main__":
    update_data()
