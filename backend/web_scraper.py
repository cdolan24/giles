import requests
from bs4 import BeautifulSoup

class WebScraper:
    def __init__(self, base_url):
        self.base_url = base_url

    def search(self, query):
        # Example: perform a GET request and parse results
        params = {'q': query}
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # This selector should be customized for each source
        results = []
        for item in soup.select('.result-item'):
            title = item.select_one('.title').get_text(strip=True)
            author = item.select_one('.author').get_text(strip=True)
            year = item.select_one('.year').get_text(strip=True)
            results.append({'title': title, 'author': author, 'year': year})
        return results

# Example usage:
# scraper = WebScraper('https://somesource.org/search')
# papers = scraper.search('quantum computing')
