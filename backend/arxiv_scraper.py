import requests
from bs4 import BeautifulSoup

class ArxivScraper:
    def __init__(self):
        self.base_url = 'https://export.arxiv.org/find/all/1/all:+AND+{query}/0/1/0/all/0/1'

    def search(self, query):
        url = self.base_url.format(query='+'.join(query.split()))
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        for item in soup.select('dt'):
            title_tag = item.find_next('dd').find('div', class_='list-title')
            title = title_tag.get_text(strip=True) if title_tag else 'No title'
            authors_tag = item.find_next('dd').find('div', class_='list-authors')
            authors = authors_tag.get_text(strip=True) if authors_tag else 'No authors'
            results.append({'title': title, 'authors': authors})
        return results

# Example usage:
# scraper = ArxivScraper()
# papers = scraper.search('quantum computing')
