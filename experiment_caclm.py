import requests
from bs4 import BeautifulSoup

def extract_caclm_bulletins():
    # Target: Cooperativas Agroalimentarias Castilla-La Mancha
    # Likely section: 'Informa' -> 'Boletines' or 'Sector Vino'
    # Start with a search or main news page related to wine.
    
    start_urls = [
        "https://www.agroalimentariasclm.coop/sector-vino",
        "https://www.agroalimentariasclm.coop/informacion/boletines",
        "https://www.fundacioncooperactiva.coop/" # Mentioned in search
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    for url in start_urls:
        print(f"\nChecking {url}...")
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                print(f"Status {response.status_code}")
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find PDF links
            links = soup.find_all('a', href=True)
            pdf_links = []
            
            print(f"Scanning {len(links)} links...")
            for l in links:
                href = l['href']
                txt = l.text.lower()
                
                # Check for relevant keywords and file type
                if ('.pdf' in href.lower()) and ('vino' in txt or 'precio' in txt or 'mercado' in txt or 'boletin' in txt):
                    full_link = href if href.startswith('http') else url.rstrip('/') + '/' + href.lstrip('/')
                    pdf_links.append((l.text.strip(), full_link))
            
            print(f"Found {len(pdf_links)} relevant PDF links:")
            for name, link in pdf_links[:5]:
                print(f"- {name}: {link}")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    extract_caclm_bulletins()
