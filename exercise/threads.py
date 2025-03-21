import requests 
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import urllib.robotparser
from urllib.parse import urlparse, urljoin

def is_allowed(url,user_agent='*'):
    parsed_url = urlparse(url)
    base_url = f'{parsed_url.scheme}://{parsed_url.netloc}'
    robots_url = urljoin(base_url, 'robots.txt')
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    rp.read()
    return rp.can_fetch(user_agent, url)

def fetch_page(url):
    if not is_allowed(url):
        print(f'Scraping not allowed for {url}')
        return None
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f'Successfully fetched {url}')
            soup = BeautifulSoup(response.content,'html.parser')
            return soup
        else:
            print(f'Failed to fetch {url} with status code {response.status_code}')
    except Exception as e:
        print(f'Exception ocurred while fetching {url}: {e}')
        
    return None

def extract_links(soup,base_url):
    links = []
    if soup:
        for link in soup.find_all('a',href=True):
            full_url = urljoin(base_url,link['href'])
            links.append(full_url)
        return links
    
    
def scrape_urls(urls,max_workers=5):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_page,url): url for url in urls}
        results = []
        for future in futures:
            result = future.result()
            if result:
                results.append(result)
            return results
        
        
def main():
    start_url = 'https://example.com'
    soup = fetch_page(start_url)
    if not soup:
        return
    
    links = extract_links(soup,start_url)
    pages = scrape_urls(links)
    
    for page in pages:
        if page:
            title = page.find('title').get_text()
            print(f'Page title:{title}')
            
if __name__ == '__main__':
    main()