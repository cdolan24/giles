import requests
from bs4 import BeautifulSoup

class ArxivScraper:
    def __init__(self):
        self.base_url = 'https://arxiv.org/search/?query={query}&searchtype=all'

    def search(self, query):
        url = self.base_url.format(query='+'.join(query.split()))
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        for item in soup.select('li.arxiv-result'):
            title_tag = item.select_one('p.list-title a')
            title = title_tag.get_text(strip=True) if title_tag else 'No title'
            authors_tags = item.select('p.authors a')
            authors = ', '.join([a.get_text(strip=True) for a in authors_tags]) if authors_tags else 'No authors'
            abstract_tag = item.select_one('span.abstract-short')
            abstract = abstract_tag.get_text(strip=True) if abstract_tag else 'No abstract'
            results.append({
                'title': title,
                'authors': authors,
                'abstract': abstract
            })
        return results

# Example usage:
# scraper = ArxivScraper()
# papers = scraper.search('quantum computing')
