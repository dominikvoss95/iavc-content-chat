import asyncio
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

INGEST_API_URL = "http://localhost:8000/ingest"

# Constants
SEED_URLS = [
    "https://www.iavcworld.de/",
    "https://www.iavcworld.de/kuenstliche-intelligenz.html",
    "https://www.iavcworld.de/news.html"
]

async def crawl_for_article_links(start_urls: list, max_links: int = 50) -> list:
    """
    Crawls given starting URLs for potential article links.
    """
    print("Searching for articles on the website...")
    found_articles = set()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for url in start_urls:
            try:
                print(f"Scanne Seite: {url}")
                response = await client.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "html.parser")
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    
                    # Relativen Link (z.B. /news/artikel1.html) in absoluten Link umwandeln
                    full_url = urljoin(url, href)
                    
                    # Nur Links zulassen, die zur iavcworld.de Hauptdomain gehören
                    parsed_url = urlparse(full_url)
                    if "iavcworld.de" not in parsed_url.netloc:
                        continue
                        
                    # Filter: Sieht der Link wie ein Artikel aus?
                    # Meistens enden echte Artikel-Seiten auf .html und sind länger
                    path = parsed_url.path
                    if path.endswith(".html") and len(path) > 15:
                        # Kategorien oder Kontakt-Seiten ausschließen, falls nötig
                        if not any(stop in path for stop in ["impressum", "datenschutz", "kontakt"]):
                            found_articles.add(full_url)
                            
                    # Wenn wir genug Links gesammelt haben, hören wir auf
                    if len(found_articles) >= max_links:
                        break
            except Exception as e:
                print(f"Error scanning {url}: {e}")
                
            if len(found_articles) >= max_links:
                break
                
    return list(found_articles)

async def ingest_article(client: httpx.AsyncClient, url: str):
    """Sends a URL to the local ingestion API."""
    print(f"\n-> Ingestion started for: {url}")
    try:
        response = await client.post(
            INGEST_API_URL, 
            json={"source_url": url, "category_name": "Crawler", "debug": False},
            timeout=60.0
        )
        if response.status_code == 200:
            data = response.json()
            chunks = data.get("indexed_chunks", 0)
            if chunks > 0:
                print(f"   [SUCCESS] {chunks} knowledge chunks added to database!")
            else:
                print(f"   [SKIPPED] Too short or invalid content.")
        else:
            print(f"   [ERROR] Status Code {response.status_code}")
    except Exception as error:
        print(f"   [ERROR] {error}")

async def run_crawler():
    """Main crawler entry point."""
    print("=== IAVC World Intelligent Auto-Crawler Started ===")
    
    urls = await crawl_for_article_links(SEED_URLS, max_links=30)
    
    print(f"\nFound {len(urls)} potential article links!")
    print("Beginning ingestion (pausing between articles to respect the host server)...\n")
    
    async with httpx.AsyncClient() as client:
        for i, url in enumerate(urls):
            print(f"[{i+1}/{len(urls)}]")
            await ingest_article(client, url)
            
            # Rate limiting to protect the father's website
            await asyncio.sleep(2)
            
    print("\n=== Crawler Finished! Knowledge stored in local database. ===")

if __name__ == "__main__":
    asyncio.run(run_crawler())
