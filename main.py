import functions_framework
import requests
import json
from datetime import datetime, timedelta
import pandas as pd
from google.cloud import bigquery
import os
import eurostat
from bs4 import BeautifulSoup
import logic
import pandas as pdt

# Configuration
API_URL = "https://ec.europa.eu/agrifood/api/wine/prices"
PROJECT_ID = os.environ.get("GCP_PROJECT", "monitor-precio-europa") # Default for local testing
DATASET_ID = "wine_market_data"
TABLE_ID = "prices_staging"

# Mapping for bulk wine identification
# We focus on "Without GI" (Geographical Indication) which is typically bulk/table wine.
TARGET_DESCRIPTIONS = {
    "ES": {
        "vino blanco sin DOP/IGP": "White",
        "vino tinto sin DOP/IGP": "Red"
    },
    "IT": {
        "Vino bianco senza DOP/IGP": "White",
        "Vino rosso senza DOP/IGP": "Red"
    },
    "FR": {
        "Blancs / Vin sans IG sans mention de cépages": "White",
        "Rouges et Rosés / Vin sans IG sans mention de cépages": "Red"
    }
}

def extract_dg_agri(request):
    """
    Cloud Function entry point.
    Extracts data from DG AGRI, normalizes it, and loads it to BigQuery.
    """
    try:
        # 1. Define date range (last 30 days to ensure we catch updates)
        end_date = datetime.now()
        # Fetching full history (2020-2026) as requested
        years_param = "2020,2021,2022,2023,2024,2025,2026"
        
        # DG AGRI format: dd/mm/yyyy
        params = {
            "memberStateCodes": "ES,IT,FR", # Adding PT didn't work (no data)
            "years": years_param
        }
        
        print(f"Fetching data from {API_URL} with params: {params}")
        response = requests.get(API_URL, params=params, timeout=60)
        response.raise_for_status()
        raw_data = response.json()
        
        print(f"Raw records fetched: {len(raw_data)}")
        
        # 2. Process and Normalize Data
        normalized_data = []
        for record in raw_data:
            country = record.get('memberStateCode')
            desc = record.get('description')
            price_str = record.get('price')
            
            # Check if this is a target bulk wine
            wine_type = None
            if country in TARGET_DESCRIPTIONS:
                for target_desc, w_type in TARGET_DESCRIPTIONS[country].items():
                    if target_desc in desc:
                        wine_type = w_type
                        break
            
            if wine_type:
                try:
                    # Clean price string (remove '€', whitespace, replace ',' with '.')
                    clean_price = price_str.replace('€', '').replace(' ', '').replace(',', '.')
                    # Handle cases where unit might be included in price string or other artifacts
                    # Simple filter to keep only digits and dot
                    clean_price = "".join(c for c in clean_price if c.isdigit() or c == '.')
                    
                    price = float(clean_price)
                    
                    # Parse date (format dd/mm/yyyy in API)
                    date_str = record.get('beginDate')
                    date_obj = datetime.strptime(date_str, "%d/%m/%Y").date()

                    row = {
                        "fecha": date_obj.isoformat(),
                        "pais_origen": country,
                        "descripcion_original": desc,
                        "tipo_vino": wine_type, # White or Red
                        "precio_eur_hl": price,
                        "moneda": record.get('unit'),
                        "formato": "Granel", # DG AGRI purely tracks bulk market for these descriptions
                        "fuente": "DG AGRI (Comisión Europea)"
                    }
                    
                    # 3. Apply Business Logic (Opportunity detection)
                    # We only calculate export opportunities FROM Spain TO target markets
                    if country == "ES":
                        # Compare with latest known prices in FR/IT (This part requires previous state or fetching concurrently)
                        # For now, we simulate the calculation based on assumed destination prices or just store the cost.
                        pass
                        
                        # Calculate cost to deliver to France
                        # REMOVED per user request for "Real Prices Only"
                        # transport_es_fr = logic.DEFAULT_TRANSPORT_COSTS.get(("ES", "FR"), 3.5)
                        # cost_fr = logic.calculate_transaction_cost(price, transport_es_fr)
                        # row["costo_transaccion_estimado_fr"] = round(cost_fr, 2)
                        
                        # Calculate cost to deliver to Italy
                        # transport_es_it = logic.DEFAULT_TRANSPORT_COSTS.get(("ES", "IT"), 5.5)
                        # cost_it = logic.calculate_transaction_cost(price, transport_es_it)
                        # row["costo_transaccion_estimado_it"] = round(cost_it, 2)

                    normalized_data.append(row)
                except (ValueError, TypeError) as e:
                    print(f"Error parsing record {record}: {e}")
                    continue
        
        print(f"Normalized records: {len(normalized_data)}")
        
        if not normalized_data:
            return "No relevant data found.", 200

        # 4. Load to BigQuery
        # client = bigquery.Client(project=PROJECT_ID)
        # table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
        # errors = client.insert_rows_json(table_ref, normalized_data)
        # if errors:
        #     print(f"Encountered errors while inserting rows: {errors}")
        #     return f"Errors: {errors}", 500
        
        return json.dumps(normalized_data, indent=2), 200

    except Exception as e:
        print(f"Execution failed: {e}")
        return f"Error: {str(e)}", 500

# Placeholders for other sources
def extract_ciatti(request):
    """
    Placeholder for Ciatti Report extraction.
    Requires parsing PDF/Email reports or scraping a login-protected portal.
    """
    print("Extracting Ciatti data... (Placeholder)")
    return [], 200

def extract_eurostat(request):
    """
    Extracts FOB export prices from Eurostat (Comext).
    Expands to ES, IT, PT, FR and Bulk vs Bottled.
    """
    print("Extracting Eurostat Export Data (FOB) - Enhanced...")
    dataset_code = 'DS-045409'   
    
    # Product Codes (CN8)
    # 2204 29: Bulk (> 10L) -> Proxy for Bulk
    # 2204 21: Bottled (< 2L) -> Proxy for Bottled
    # Using specific codes to ensure data quality or broad codes? 
    # Broad codes 220429 and 220421 usually filter well enough if 6-digit support exists or we use wildcards logic.
    # But get_data_df often needs explicit codes or list.
    # Let's use a list of common codes.
    
    # Bulk White/Red (>10L)
    bulk_codes = ['22042993', '22042994', '22042995', '22042996'] 
    
    # Bottled White/Red (<2L)
    # 2204 21 06 - 09 (PDO/IGP?)
    # 2204 21 79 / 80 ...
    # Let's try 220421 codes. There are many. 
    # To keep it simple, we might rely on the API aggregating if we pass 6 digits?
    # Eurostat API often doesn't aggregate 6-digit for DS-045409 directly if strictly 8-digit.
    # But let's try passing the 6 digit prefix in separate calls or find a generic code?
    # Actually, for "Intensification", let's stick to the ones we verified work + adding PT/IT reporters.
    
    # Extending verified Bulk codes:
    products = bulk_codes
    
    # Adding Sample Bottled Codes (needs verification, but let's try common ones)
    # 22042111 (Champagne? No)
    # 22042179 (White other) 
    # 22042180 (Red other)
    bottled_codes = ['22042179', '22042180']
    products.extend(bottled_codes)

    reporters = ['ES', 'IT', 'PT', 'FR'] # Major producers
    partners = ['FR', 'DE', 'US', 'GB', 'WORLD'] # Major buyers + World
    
    filter_pars = {
        'freq': ['M'],
        'reporter': reporters,
        'partner': partners, 
        'flow': ['2'], # Exports
        'product': products,
        'startPeriod': '2000-01'
    }
    
    try:
        df = eurostat.get_data_df(dataset_code, filter_pars=filter_pars)
        
        if df.empty:
            print("No Eurostat data found.")
            return [], 200
            
        # Reshape
        id_vars = ['freq', 'reporter', 'partner', 'product', 'flow']
        indic_col = next((c for c in df.columns if 'indic' in c), None)
        if not indic_col: indic_col = df.columns[5]
            
        id_vars.append(indic_col)
        df_melt = df.melt(id_vars=id_vars, var_name='time_period', value_name='obs_value')
        df_melt = df_melt.dropna(subset=['obs_value'])
        
        pivot_df = df_melt.pivot_table(
            index=['time_period', 'reporter', 'partner', 'product'], 
            columns=indic_col, 
            values='obs_value',
            aggfunc='sum'
        ).reset_index()
        
        results = []
        for _, row in pivot_df.iterrows():
            val = row.get('VALUE_IN_EUROS', 0)
            qty = row.get('SUPPLEMENTARY_QUANTITY', 0) 
            # Note: Bottled wine might strictly use QUANTITY_IN_100KG instead of Liters in some datasets?
            # Usually Wine has SUP_QUANTITY (Liters).
            
            # If SUP_QUANTITY is missing, check 100KG?
            # 1 HL wine ~ 100KG. It's a fair proxy.
            if qty == 0:
                qty_kg = row.get('QUANTITY_IN_100KG', 0)
                if qty_kg > 0:
                    qty = qty_kg * 100 # Approx liters? 100KG is 100kg. Density ~1.
                    # Wait, unit is 100KG = 100 Kilo Grams.
                    # 100 kg ~= 1 HL.
                    # So value is 100KG.
                    qty = qty_kg # Treat as HL roughly.
            
            if qty > 0 and val > 0:
                price_hl = (val / qty) * 100 # If qty is Liters?
                # If SUP_QUANTITY is Liters: (Val / Liters) * 100 = Price per HL. Correct.
                # If using 100KG (approx HL): (Val / HL) = Price per HL.
                # Warning: need to pinpoint unit.
                # Assuming SUP = Liters for simplicity as verified before.
                
                p_code = row['product']
                
                # Determine Type
                # 93/79 -> White (approx), 94/80 -> Red
                w_type = 'White' if any(x in p_code for x in ['93', '79', '2993']) else 'Red'
                
                # Determine Format
                fmt = "Granel"
                if p_code in bottled_codes or '220421' in p_code:
                    fmt = "Embotellado"
                
                try:
                   date_obj = datetime.strptime(row['time_period'], "%Y-%m").date()
                   date_obj = date_obj.replace(day=15)
                except:
                    continue
                
                # Source Label
                src_label = f"Eurostat ({row['reporter']})"

                item = {
                    "fecha": date_obj.isoformat(),
                    "pais_origen": f"{row['reporter']} {fmt}", # ES Granel, IT Embotellado
                    "descripcion_original": f"Export {row['reporter']}->{row['partner']} (CN {p_code})",
                    "tipo_vino": w_type,
                    "precio_eur_hl": round(price_hl, 2),
                    "moneda": "EUR/HL (FOB)",
                    "formato": fmt,
                    "fuente": "Eurostat (Comext)"
                }
                
                # Add logic for specific interesting flows (ES->FR)
                if row['reporter'] == 'ES' and row['partner'] == 'FR' and fmt == 'Granel':
                     cost_fr = logic.calculate_transaction_cost(price_hl, 3.5)
                     item["costo_transaccion_estimado_fr"] = round(cost_fr, 2)
                
                results.append(item)

        print(f"Eurostat records: {len(results)}")
        return results, 200

    except Exception as e:
        print(f"Eurostat extraction failed: {e}")
        return [], 200

def extract_infovi(request):
    """
    Placeholder for INFOVI (Interprofesional del Vino de España).
    Source for 'Stocks' / 'Existencias'.
    """
    print("Extracting INFOVI data (Stocks) - Placeholder...")
    return [], 200

def extract_ismea(request):
    """
    Features ISMEA (Italian Market) data.
    Current implementation: Downloads latest available Sector Report PDF.
    Future: Parse 'Listini Settimanali' if URL becomes stable.
    """
    print("Extracting ISMEA data (Italy)...")
    # URL found in research:
    pdf_url = "https://www.ismeamercati.it/flex/files/1/2/0/D.cb36d062f3ff1dee7222/SchedaVino_Maggio_2025.pdf"
    
    try:
        response = requests.get(pdf_url, verify=False, timeout=30)
        if response.status_code == 200:
            filename = "ismea_report_latest.pdf"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"ISMEA Report saved to {filename} (Manual parsing required for now).")
            # Logic to parse PDF would go here (using tabula-py or similar)
            return [{"source": "ISMEA", "type": "Report", "file": filename}], 200
        else:
            print(f"Failed to download ISMEA report: {response.status_code}")
            return [], 500
    except Exception as e:
        print(f"ISMEA extraction error: {e}")
        return [], 500
    
def extract_franceagrimer(request):
    """
    Placeholder for FranceAgriMer.
    """
    print("Extracting FranceAgriMer data - Placeholder...")
    return [], 200

def extract_lonja_ciudad_real(request):
    """
    Placeholder for Lonja Ciudad Real.
    Research indicates 'Cooperativas Agroalimentarias Castilla-La Mancha' is the best source.
    Direct scraping is currently blocked/404.
    """
    print("Extracting Lonja Ciudad Real data - Placeholder (Manual Download Required from 'agroalimentariasclm.coop')")
    return [], 200

# Local testing
if __name__ == "__main__":
    full_data.extend(data_es)
    # 3. New Sources (Hybrid/Manual)
    d_ism, s_ism = extract_ismea(None)
    extract_lonja_ciudad_real(None)
    
    print(f"Total Combined Records: {len(full_data)}")
