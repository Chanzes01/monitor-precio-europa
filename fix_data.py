import json

try:
    with open('latest_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    with open('data.js', 'w', encoding='utf-8') as f:
        f.write('const WINE_DATA = ')
        json.dump(data, f, indent=2)
        f.write(';')
        
    print("Success: data.js updated.")
except Exception as e:
    print(f"Error: {e}")
