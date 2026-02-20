import requests
from bs4 import BeautifulSoup
import pandas as pd

def extract_ismea_prices():
    # Target: Indice prezzi or BD prezzi
    # Found in previous step: https://www.ismeamercati.it/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/1947
    
    url = "https://www.ismeamercati.it/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/1947"
    
    print(f"Fetching ISMEA Prices from {url}...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0'
        }
        response = requests.get(url, headers=headers, verify=False, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for tables
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables.")
        
        if len(tables) > 0:
            # Parse first table
            df = pd.read_html(str(tables[0]))[0]
            print("Table 1 Sample:")
            print(df.head())
            
            # Check for wine keywords
            wine_rows = df[df.astype(str).apply(lambda x: x.str.contains('vino|Vino', case=False)).any(axis=1)]
            print(f"\nPotential Wine Rows: {len(wine_rows)}")
            if not wine_rows.empty:
                print(wine_rows.head())
        else:
            print("No tables found. Page structure might be div-based or require navigation.")
            # Check for links to actual data
            links = soup.find_all('a')
            print("Checking links for 'download' or 'xls'...")
            for l in links:
                if 'scarica' in l.text.lower() or 'xls' in str(l.get('href')):
                    print(f"Download link: {l.text} -> {l.get('href')}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_ismea_prices()
