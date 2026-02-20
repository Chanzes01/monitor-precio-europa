import requests
from bs4 import BeautifulSoup
import pandas as pd

def extract_ismea_abs_prices():
    # Attempting to find absolute prices (EUR/HL) instead of Index
    # Candidates from previous crawl:
    # IDPagina/489 and 547 were found.
    
    candidates = [
        "http://www.ismeamercati.it/vino",
        "http://www.ismeamercati.it/fasi-di-scambio/origine",
        "http://www.ismeamercati.it/fasi-di-scambio/ingrosso"
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    for url in candidates:
        print(f"\n--- Checking {url} ---")
        try:
            response = requests.get(url, headers=headers, verify=False, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for download links
            links = soup.find_all('a', href=True)
            downloads = [l for l in links if '.xls' in l['href'].lower() or '.pdf' in l['href'].lower() or 'scarica' in l.text.lower()]
            
            print(f"Found {len(downloads)} download links.")
            for d in downloads[:10]:
                 print(f"- {d.text.strip()}: {d['href']}")
                    
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    extract_ismea_abs_prices()
