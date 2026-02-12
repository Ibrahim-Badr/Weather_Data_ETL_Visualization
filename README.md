# 🌤️ Weather Data ETL & Visualization

![CI/CD Status](https://github.com/ibrahim-badr/Weather_Data_ETL_Visualization/actions/workflows/python-app.yml/badge.svg)
![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)
![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen.svg)
![Tests](https://img.shields.io/badge/tests-122%20passed-success.svg)

## 📊 Project Overview

Professional ETL (Extract, Transform, Load) pipeline for Toulouse weather data with REST API and interactive web dashboard. Built as a comprehensive data engineering project demonstrating industry best practices.

### Key Features

- ✅ **ETL Pipeline**: Automated data extraction from Toulouse Open Data API
- ✅ **Data Structures**: Binary Search Tree, Hash Table, Linked List implementations
- ✅ **Design Patterns**: Strategy, Factory, Singleton, Observer, Decorator patterns
- ✅ **REST API**: FastAPI with OpenAPI documentation
- ✅ **Interactive Dashboard**: Real-time weather visualization with Chart.js
- ✅ **Testing**: 122 unit tests with 85% code coverage
- ✅ **Docker**: Multi-service containerized deployment
- ✅ **CI/CD**: Automated testing and deployment with GitHub Actions

---

## 🏗️ Architecture

```text
┌─────────────────────────────────────────────────────────┐
│                    ETL Pipeline                          │
├─────────────────────────────────────────────────────────┤
│  Extractor → Transformer → Loader → SQLite Database     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│                   FastAPI REST API                       │
├─────────────────────────────────────────────────────────┤
│  /health  │  /stations  │  /weather  │  /docs           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│            Interactive Web Dashboard                     │
├─────────────────────────────────────────────────────────┤
│  Charts │ Statistics │ Filters │ CSV Export             │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```text
Weather_Data_ETL_Visualization/
├── .github/
│   └── workflows/
│       └── python-app.yml          # CI/CD pipeline
├── database/
│   └── weather.db                  # SQLite database
├── src/
│   ├── api/
│   │   ├── main.py                # FastAPI application
│   │   ├── dependencies.py        # Dependency injection
│   │   └── routes/
│   │       ├── health.py          # Health check endpoint
│   │       ├── stations.py        # Stations endpoints
│   │       └── weather.py         # Weather data endpoints
├── src/
│   ├── config/
│   │   └── settings.py            # Configuration management
│   ├── extractors/
│   │   ├── interface.py           # Extractor interface
│   │   └── api_extractor.py      # API data extraction
│   ├── loaders/
│   │   ├── interface.py           # Loader interface
│   │   └── database_loader.py    # SQLite loader
│   ├── models/
│   │   └── weather_data.py       # Data models (Pydantic)
│   ├── pipeline/
│   │   └── etl_pipeline.py       # Main pipeline orchestration
│   ├── services/
│   │   └── station_selector.py   # Station selection logic
│   ├── structures/
│   │   ├── binary_search_tree.py # BST implementation
│   │   ├── hash_table.py         # Hash table implementation
│   │   └── linked_list.py        # Linked list implementation
│   └── transformers/
│       ├── interface.py           # Transformer interface
│       └── data_transformer.py    # Data cleaning & validation
├── static/
│   └── index.html                 # Dashboard frontend
├── tests/
│   ├── test_api/                  # API tests
│   ├── test_extractors/           # Extractor tests
│   ├── test_loaders/              # Loader tests
│   ├── test_models/               # Model tests
│   ├── test_pipeline/             # Pipeline tests
│   ├── test_services/             # Service tests
│   ├── test_structures/           # Data structure tests
│   └── test_transformers/         # Transformer tests
├── docker-compose.yml             # Docker orchestration
├── Dockerfile                     # Docker image definition
├── main.py                        # CLI entry point
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (optional)
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/Weather_Data_ETL_Visualization.git
cd Weather_Data_ETL_Visualization
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

---

## 💻 Usage

### Option 1: Local Development

#### Run ETL Pipeline
```bash
# List available stations
python main.py --list-stations

# Extract data for specific stations
python main.py --stations 24 25 26 --limit 100

# Extract all stations
python main.py --limit 200
```

#### Start API Server
```bash
uvicorn src.api.main:app --reload

# API available at:
# - http://localhost:8000
# - Docs: http://localhost:8000/docs
# - Dashboard: http://localhost:8000/dashboard
```

#### Run Tests
```bash
# Run all tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

---

### Option 2: Docker Deployment

#### Build and Start Services
```bash
# Build images
docker compose build

# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f

# Stop services
docker compose down
```

#### Access Services
- **Dashboard**: http://localhost:8000/dashboard
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 🔌 API Endpoints

### Health Check
`GET /health`

**Response:**
```json
{
  "status": "healthy",
  "records": 4523,
  "stations": 44
}
```

### List Stations
`GET /stations?limit=10&offset=0`

### Get Weather Data
`GET /weather/?station_id=24&limit=100&start_date=2020-01-01&end_date=2024-12-31`

### Get Statistics
`GET /weather/statistics/?station_id=24`

---

## 📊 Dashboard Features

- **Interactive Charts**: Temperature, humidity, rainfall, wind, pressure
- **Real-time Filtering**: Filter by date range
- **Station Selection**: 44 weather stations in Toulouse
- **Statistics**: Average, min/max, totals
- **CSV Export**: Download filtered data

---

## 🧪 Testing

### Test Coverage
- **Total Tests**: 122
- **Coverage**: 85%
- **Test Types**: Unit, Integration, API

### Run Tests
```bash
# All tests
pytest -v

# Specific module
pytest tests/test_api/ -v

# With coverage
pytest --cov=src --cov-report=term-missing

# Generate HTML report
pytest --cov=src --cov-report=html
```

---

## 🏛️ Design Patterns Used

1. **Strategy Pattern**: Interchangeable extractors/loaders
2. **Factory Pattern**: Station selector creation
3. **Singleton Pattern**: Configuration management
4. **Observer Pattern**: Pipeline event notifications
5. **Decorator Pattern**: Data validation decorators

---

## 📚 Data Structures Implemented

### 1. Binary Search Tree
- **File**: `src/structures/binary_search_tree.py`
- **Use Case**: Efficient station lookup by ID
- **Complexity**: $O(\log n)$ search

### 2. Hash Table
- **File**: `src/structures/hash_table.py`
- **Use Case**: Fast station metadata retrieval
- **Complexity**: $O(1)$ average case

### 3. Linked List
- **File**: `src/structures/linked_list.py`
- **Use Case**: Weather data time series
- **Complexity**: $O(1)$ insertion

---

## 🐳 Docker Services

| Service | Description | Port |
| :--- | :--- | :--- |
| **database** | SQLite volume container | - |
| **etl** | ETL pipeline runner | - |
| **api** | FastAPI REST API | 8000 |

---

## ⚙️ CI/CD (GitHub Actions)

This project includes an automated CI/CD pipeline using GitHub Actions to ensure code quality and deployment reliability.

### Workflow Configuration
- **File**: `.github/workflows/python-app.yml`
- **Triggers**: 
  - Automatically on each push to: `main`, `master`, `develop`
  - Automatically on each pull request targeting: `main`, `master`

### Pipeline Steps
1. **Environment Setup**: Install dependencies using Python 3.11 with pip caching.
2. **Data Initialization**: Run ETL once with a limited dataset to populate the SQLite database.
3. **Linting**: Static code analysis with `pylint` (requires a minimum score of 7.0).
4. **Formatting**: Check code style with `black` (non-blocking).
5. **Testing**: Execute full test suite with `pytest` and generate coverage reports (minimum 80% coverage required).
6. **Containerization**: Build Docker images and verify service orchestration with `docker compose`.
7. **Health Check**: Validate the live API status via the `/health` endpoint.

### Monitoring
To view the status and history of pipeline runs, navigate to the **Actions** tab in the GitHub repository.

---

## 🔧 Configuration

### Environment Variables
```bash
DATABASE_PATH=database/weather.db
API_PORT=8000
LOG_LEVEL=info
```

### Settings
Edit `src/config/settings.py` for:
- API base URLs
- Database paths
- Logging configuration
- Rate limiting

---

## 📈 Performance

| Metric | Value |
| :--- | :--- |
| **ETL Speed** | ~500 records/min |
| **API Response Time** | <100ms (avg) |
| **Database Size** | ~5 MB (4500 records) |
| **Docker Image** | ~940 MB |
| **Test Execution** | ~25 seconds |

---

## 👨‍💻 Author

**Your Name**
- GitHub: [@Ibrahim-Badr](https://github.com/Ibrahim-Badr)

---

