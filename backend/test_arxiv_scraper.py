from arxiv_scraper import ArxivScraper

if __name__ == "__main__":
    scraper = ArxivScraper()
    papers = scraper.search("quantum computing")
    for paper in papers[:5]:
        print(f"Title: {paper['title']}")
        print(f"Authors: {paper['authors']}")
        print(f"Abstract: {paper['abstract'][:120]}...")
        print()
