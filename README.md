
# Giles: UC Library Web-Scraper Agent

---
**Status:** All base and advanced features are implemented and tested. See `expanded_implementation_plan.md` for details.

## Features
- Modular FastAPI backend with MCP resource wrappers for libraries
- React frontend chat widget and filters
- Browser extension popup for chat and search
- Citation management and export (Zotero, EndNote, BibTeX)
- Prerequisite recommender and ranking engine
- Entity linker for cross-source aggregation
- Multi-language support (backend complete, frontend UI in progress)
- Accessibility features
- User authentication and profiles
- Usage analytics dashboard
- Comprehensive unit tests for backend modules

## Quickstart

### Backend (API server)
1. Install dependencies:
	```
	pip install fastapi uvicorn requests passlib pyjwt python-multipart
	```
2. Run the backend server:
	```
	python backend/app.py
	```
   Or use Docker for production (see `deployment/docker_backend_plan.md`).

### Frontend (React app)
1. Install dependencies:
	```
	cd frontend
	npm install
	```
2. Start the frontend app:
	```
	npm start
	```

### Extension
1. Load the `extension` folder as an unpacked extension in your browser.
2. The extension connects to the backend API and provides a chat/search interface.


## Deployment
- See `deployment/docker_backend_plan.md` and `deployment/run_backend_production.md` for containerization and production setup.
- Use environment variables for secrets (see `deployment/env_vars_and_secrets.md`).

---
**Note:** Tabbed launching in Windows Terminal is still a to-do. The current script launches backend and frontend in separate windows for reliability. If you want tabbed launching, revisit this after further testing or Windows Terminal updates.

**Troubleshooting:** If the backend is running but not responding to frontend/API requests, check:
- The backend logs for error codes (see recent error handling additions)
- That your MCPResource and web scraper are correctly configured and reachable
- That your config uses a valid endpoint or the web scraper selectors match the actual HTML structure

## Configuration
- Add library connectors in `backend/config.example.json`.
- Schema in `backend/config.schema.json`.

## Agent & Library Access
- The agent is implemented as a modular backend (FastAPI) and browser extension.
- Access to the UC Library is via API connectors (see config and MCPResource setup).
- You must provide a valid UC Library API key for live data access.

## Documentation
- See `expanded_implementation_plan.md` for implementation details.
- See `product_philosophy.md` for design philosophy and user stories.
- See `session_logs/session_log.md` for progress logs.

---
For questions or further development, refer to the handoff document and session log.
