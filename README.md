# Search Engine Project

## Overview
A powerful, multi-provider search engine with advanced retrieval capabilities, caching, and API support.

## Features
- Multi-mode search (fast, balanced, quality)
- Redis-backed caching
- FastAPI endpoint
- Web scraping across multiple providers
- Vector-based and keyword-based retrieval

## Prerequisites
- Python 3.10+
- Redis server
- Virtual environment recommended

## Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/searchEngine.git
cd searchEngine
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Create a `.env` file in the project root with:
```
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
```

### 5. Run the Application
#### Start API Server
```bash
uvicorn searchEngine.api.route:app --reload
```

#### Run Search Directly
```bash
python -m searchEngine.engine.manager
```

## API Endpoints
- `POST /search`: Perform a search
- `GET /health`: Check API status

## Search Modes
- `fast`: Keyword-based retrieval
- `balanced`: Vector store retrieval
- `quality`: Ensemble retrieval

## Contributing
1. Fork the repository
2. Create your feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request

## License
MIT License
