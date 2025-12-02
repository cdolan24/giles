import json
import os
from mcp_resource import MCPResource
from web_scraper import WebScraper

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.example.json')

class SourceManager:
    def __init__(self, config_path=CONFIG_PATH):
        self.config_path = config_path
        self.sources = self.load_sources()

    def load_sources(self):
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        sources = []
        for lib in config.get('libraries', []):
            api_key = lib.get('apiKey')
            name = lib.get('name')
            base_url = lib.get('baseUrl')
            enabled = lib.get('enabled', True)
            backup_scraper = lib.get('backupScraper')
            sources.append({
                'name': name,
                'api_key': api_key,
                'base_url': base_url,
                'enabled': enabled,
                'backup_scraper': backup_scraper
            })
        return sources

    def add_source(self, name, api_key, base_url, backup_scraper=None, enabled=True):
        new_source = {
            'name': name,
            'apiKey': api_key,
            'baseUrl': base_url,
            'enabled': enabled,
            'backupScraper': backup_scraper
        }
        with open(self.config_path, 'r+') as f:
            config = json.load(f)
            config['libraries'].append(new_source)
            f.seek(0)
            json.dump(config, f, indent=2)
            f.truncate()
        self.sources.append(new_source)
        print(f"Source '{name}' added.")

    def list_sources(self):
        for src in self.sources:
            print(f"Name: {src['name']}, API Key: {src['api_key']}, Base URL: {src['base_url']}, Enabled: {src['enabled']}")
            if src['backup_scraper']:
                print(f"  Backup Scraper: {src['backup_scraper']}")

# Example usage:
# mgr = SourceManager()
# mgr.add_source('arXiv', 'arxiv-key', 'https://api.arxiv.org', backup_scraper='arxiv_scraper')
# mgr.list_sources()
