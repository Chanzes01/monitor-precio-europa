import requests
from bs4 import BeautifulSoup

def test_ismea():
    # Target URL for ISMEA Mercati - Wine sector
    # Usually: http://www.ismeamercati.it/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/1
    # or specific wine pages. Let's try a general entry point or search.
    url = "http://www.ismeamercati.it/vino"
    
    print(f"Attempting to fetch {url}...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Disable SSL verification due to certificate error
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        response.raise_for_status()
        
        print("Connection successful.")
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"Page Title: {soup.title.string.strip() if soup.title else 'No Title'}")
        
        # Look for table links or price indicators
        links = soup.find_all('a', href=True)
        print(f"Found {len(links)} links. Searching for 'prezzi' or 'listini'...")
        
        relevant = [l for l in links if 'prezzi' in l.text.lower() or 'listini' in l.text.lower()]
        for l in relevant[:5]:
            print(f"- {l.text.strip()}: {l['href']}")
            
    except Exception as e:
        print(f"Error accessing ISMEA: {e}")

if __name__ == "__main__":
    test_ismea()
