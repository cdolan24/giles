import re
import requests
from bs4 import BeautifulSoup

REQUEST_TIMEOUT = 15


class ArxivScraper:
    """HTML scraper for arxiv.org search; used as the backup when the arXiv API fails."""

    def __init__(self):
        self.base_url = 'https://arxiv.org/search/'

    def search(self, query):
        response = requests.get(self.base_url, params={'query': query, 'searchtype': 'all'}, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return self.parse(response.text)

    def parse(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        for item in soup.select('li.arxiv-result'):
            title_tag = item.select_one('p.title')
            link_tag = item.select_one('p.list-title a')
            if not title_tag:
                continue
            authors = ', '.join(a.get_text(strip=True) for a in item.select('p.authors a'))
            abstract_tag = item.select_one('span.abstract-full') or item.select_one('span.abstract-short')
            abstract = abstract_tag.get_text(' ', strip=True).replace('△ Less', '').strip() if abstract_tag else ''
            submitted = item.select_one('p.is-size-7')
            year_match = re.search(r'\b(19|20)\d{2}\b', submitted.get_text()) if submitted else None
            results.append({
                'title': title_tag.get_text(' ', strip=True),
                'author': authors,
                'year': int(year_match.group(0)) if year_match else None,
                'journal': 'arXiv',
                'abstract': abstract,
                'url': link_tag['href'] if link_tag and link_tag.has_attr('href') else '',
                'open_access': True,
            })
        return results

# Example usage:
# scraper = ArxivScraper()
# papers = scraper.search('quantum computing')
