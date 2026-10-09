import requests
from bs4 import BeautifulSoup

REQUEST_TIMEOUT = 15


def _text(item, selector):
    el = item.select_one(selector)
    return el.get_text(strip=True) if el else ''


class WebScraper:
    # Selectors should be customized for each source
    result_selector = '.result-item'
    title_selector = '.title'
    author_selector = '.author'
    year_selector = '.year'

    def __init__(self, base_url):
        self.base_url = base_url

    def search(self, query):
        response = requests.get(self.base_url, params={'q': query}, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return self.parse(response.text)

    def parse(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        for item in soup.select(self.result_selector):
            title = _text(item, self.title_selector)
            if not title:
                continue
            year = _text(item, self.year_selector)
            results.append({
                'title': title,
                'author': _text(item, self.author_selector),
                'year': int(year) if year.isdigit() else None,
            })
        return results

# Example usage:
# scraper = WebScraper('https://somesource.org/search')
# papers = scraper.search('quantum computing')
