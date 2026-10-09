"""
Loads library sources from config and builds MCP resources for them.

Config is read from GILES_CONFIG if set, else backend/config.json if present,
else backend/config.example.json. API keys are read from the environment
variable named by each library's "apiKeyEnv", falling back to "apiKey".
"""
import json
import os
import logging
from backend.mcp_resource import MCPResource
from backend.arxiv_resource import ArxivResource
from backend.arxiv_scraper import ArxivScraper
from backend.uc_library_scraper import UCLibraryScraper

BACKEND_DIR = os.path.dirname(__file__)
LOCAL_CONFIG_PATH = os.path.join(BACKEND_DIR, 'config.json')
EXAMPLE_CONFIG_PATH = os.path.join(BACKEND_DIR, 'config.example.json')

RESOURCE_TYPES = {'rest': MCPResource, 'arxiv': ArxivResource}
SCRAPERS = {'arxiv_scraper': ArxivScraper, 'uc_library_scraper': UCLibraryScraper}


def default_config_path():
    if os.environ.get('GILES_CONFIG'):
        return os.environ['GILES_CONFIG']
    return LOCAL_CONFIG_PATH if os.path.exists(LOCAL_CONFIG_PATH) else EXAMPLE_CONFIG_PATH


class SourceManager:
    def __init__(self, config_path=None):
        self.config_path = config_path or default_config_path()
        self.sources = self.load_sources()

    def load_sources(self):
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        sources = []
        for lib in config.get('libraries', []):
            key_env = lib.get('apiKeyEnv')
            sources.append({
                'name': lib.get('name'),
                'type': lib.get('type', 'rest'),
                'api_key': (os.environ.get(key_env) if key_env else None) or lib.get('apiKey') or None,
                'base_url': lib.get('baseUrl'),
                'enabled': lib.get('enabled', True),
                'backup_scraper': lib.get('backupScraper')
            })
        return sources

    def build_resources(self):
        resources = []
        for src in self.sources:
            if not src['enabled']:
                logging.info(f"Source '{src['name']}' is disabled in {self.config_path}")
                continue
            resource_cls = RESOURCE_TYPES.get(src['type'])
            if resource_cls is None:
                logging.error(f"Source '{src['name']}' has unknown type '{src['type']}'; skipping")
                continue
            scraper_cls = SCRAPERS.get(src['backup_scraper'])
            if src['backup_scraper'] and scraper_cls is None:
                logging.warning(f"Source '{src['name']}' names unknown backup scraper '{src['backup_scraper']}'")
            resources.append(resource_cls(
                name=src['name'],
                base_url=src['base_url'],
                api_key=src['api_key'],
                backup_scraper=scraper_cls() if scraper_cls else None
            ))
        return resources

    def add_source(self, name, base_url, api_key_env=None, backup_scraper=None, enabled=True, source_type='rest'):
        new_source = {
            'name': name,
            'type': source_type,
            'baseUrl': base_url,
            'apiKeyEnv': api_key_env,
            'enabled': enabled,
            'backupScraper': backup_scraper
        }
        with open(self.config_path, 'r+') as f:
            config = json.load(f)
            config['libraries'].append(new_source)
            f.seek(0)
            json.dump(config, f, indent=2)
            f.truncate()
        self.sources = self.load_sources()
        print(f"Source '{name}' added.")

    def list_sources(self):
        for src in self.sources:
            key_status = 'set' if src['api_key'] else 'not set'
            print(f"Name: {src['name']}, Type: {src['type']}, API Key: {key_status}, Base URL: {src['base_url']}, Enabled: {src['enabled']}")
            if src['backup_scraper']:
                print(f"  Backup Scraper: {src['backup_scraper']}")

# Example usage:
# mgr = SourceManager()
# mgr.add_source('CERN', 'https://cds.cern.ch/api', api_key_env='API_KEY_CERN')
# mgr.list_sources()
