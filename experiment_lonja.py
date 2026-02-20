import requests
from bs4 import BeautifulSoup

def test_lonja():
    # Lonja Agropecuaria de Ciudad Real
    # Official or aggregator?
    # Globalcaja sometimes publishes it, or specialized sites like 'Agrocomparador' or 'Camara Ciudad Real'.
    # Let's try a common aggregator for test: 'Precios de Lonjas' or similar if official is hard to find.
    # Searching for a representative URL.
    # hypothetical: https://www.camaracr.org/lonja-agropecuaria/mesa-del-vino
    
    urls = [
        "https://www.camaracr.org/servicios/lonja/mesas-de-precios",
        "https://www.camaracr.org/lonja/mesas-de-precios" # Try alternative
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for url in urls:
        print(f"Attempting to fetch {url}...")
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                print(f"Success connecting to {url}")
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Inspect all links for PDF or documents
                print(f"Scanning {url} for content...")
                all_links = soup.find_all('a', href=True)
                pdf_links = [l['href'] for l in all_links if '.pdf' in l['href'].lower()]
                print(f"Found {len(pdf_links)} PDF links.")
                for pdf in pdf_links:
                    print(f"- {pdf}")
                
                # Check iframes (sometimes content is embedded)
                iframes = soup.find_all('iframe')
                print(f"Found {len(iframes)} iframes.")
                for i in iframes:
                    print(f"- Iframe src: {i.get('src')}")
                
                # Check for any "Mesa del Vino" specific link again
                relevant = [l for l in all_links if 'vino' in l.text.lower()]
                for r in relevant:
                    print(f"- Relevant Link: {r.text.strip()} -> {r['href']}")
                    
            else:
                print(f"Status {response.status_code} for {url}")
        except Exception as e:
            print(f"Error accessing {url}: {e}")

if __name__ == "__main__":
    test_lonja()
