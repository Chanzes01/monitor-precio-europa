import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def crawl_ismea():
    base_url = "http://www.ismeamercati.it"
    start_url = "http://www.ismeamercati.it/vino"
    
    visited = set()
    queue = [start_url]
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    print(f"Starting crawl from {start_url}...")
    
    # Limit depth/count
    count = 0
    max_pages = 20
    
    candidates = []
    
    while queue and count < max_pages:
        url = queue.pop(0)
        if url in visited: continue
        visited.add(url)
        count += 1
        
        try:
            print(f"[{count}] Crawling {url}...")
            response = requests.get(url, headers=headers, verify=False, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for content keywords in this page
            page_text = soup.get_text().lower()
            if 'settimanale' in page_text or 'listino' in page_text:
                print(f"  -> Found keywords in {url}")
                candidates.append((soup.title.string.strip() if soup.title else url, url))
            
            # Find links
            for a in soup.find_all('a', href=True):
                href = a['href']
                full_url = urljoin(base_url, href)
                 
                # Only follow internal wine-related links
                if base_url in full_url and ('vino' in full_url or 'prezzi' in full_url or 'mercati' in full_url):
                    if full_url not in visited:
                        queue.append(full_url)
                        
        except Exception as e:
            print(f"  -> Error: {e}")

    print("\n--- Best Candidates for Weekly Prices ---")
    for title, link in candidates:
        print(f"{title}: {link}")

if __name__ == "__main__":
    crawl_ismea()
