
import json
from datetime import datetime, timedelta

def add_projections():
    with open('latest_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1. Find latest prices for each category
    latest_prices = {}
    for row in data:
        key = (row.get('pais_origen'), row.get('tipo_vino'), row.get('formato'))
        date_str = row.get('fecha')
        if not date_str: continue
        
        if key not in latest_prices or date_str > latest_prices[key]['fecha']:
            latest_prices[key] = row

    # 2. Generate Projections for 2026
    projections = []
    dates_2026 = ['2026-01-15', '2026-02-15']
    
    print(f"Found {len(latest_prices)} unique series. Generating projections for {dates_2026}...")

    for key, last_row in latest_prices.items():
        price = last_row.get('precio_eur_hl')
        if price is None: continue
        
        # Simple projection: assume stable or slight trend? 
        # Let's keep it stable for now to avoid misleading, but mark as projection.
        for d in dates_2026:
            new_row = last_row.copy()
            new_row['fecha'] = d
            new_row['precio_eur_hl'] = price # Flat projection
            new_row['fuente'] = "Proyección Antigravity (2026)"
            new_row['descripcion_original'] = last_row.get('descripcion_original', '') + " (Proyección)"
            
            # Add to list
            projections.append(new_row)

    # 3. Append and Save
    print(f"Adding {len(projections)} projection records.")
    data.extend(projections)
    
    # Sort by date desc
    data.sort(key=lambda x: x.get('fecha', ''), reverse=True)

    with open('latest_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    with open('data.js', 'w', encoding='utf-8') as f:
        f.write(f"const WINE_DATA = {json.dumps(data, indent=2)};")

    print("Successfully added 2026 projections.")

if __name__ == "__main__":
    add_projections()
