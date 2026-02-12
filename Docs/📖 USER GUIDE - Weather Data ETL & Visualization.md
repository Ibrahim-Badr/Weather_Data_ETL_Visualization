# 📖 USER GUIDE - Weather Data ETL & Visualization

---

## 📋 TABLE OF CONTENTS

1. [Running the ETL Pipeline](#1-running-the-etl-pipeline)
2. [Using the API](#2-using-the-api)
3. [Dashboard Guide](#3-dashboard-guide)
4. [Running Tests](#4-running-tests)
5. [Advanced Usage](#5-advanced-usage)
6. [FAQ](#6-faq)

---

## 1. RUNNING THE ETL PIPELINE

The ETL pipeline extracts weather data from the Toulouse Open Data API, transforms and cleans it, then loads it into a SQLite database.

### Basic Commands
```bash
# List all available weather stations
python main.py --list-stations

# Extract data for specific stations
python main.py --stations 24 25 26

# Extract with record limit
python main.py --stations 24 --limit 100

# Extract all stations (takes longer)
python main.py --limit 200

# Get help
python main.py --help
```

### Command Line Options
| Option | Description |
| :--- | :--- |
| `--list-stations` | List all available stations |
| `--stations IDs` | Comma-separated station IDs (e.g., 24,25,26) |
| `--limit N` | Maximum records per station (default: 1000) |
| `--help` | Show help message |

### Example Workflow
1. **List stations to find IDs**:
   ```bash
   python main.py --list-stations
   ```
   *Output shows station info:*
   ```text
   Station ID: 24
   Name: 24-station-meteo-colomiers-zi-enjacca
   Location: Toulouse
   ────────────────────────────────────────────
   ```

2. **Extract data for selected stations**:
   ```bash
   python main.py --stations 24 25 --limit 100
   ```

3. **Verify database was created**:
   - **Windows**: `dir database\weather.db`
   - **Linux/Mac**: `ls -lh database/weather.db`

### ETL Pipeline Stages
1. **EXTRACT**
   - Fetches data from Toulouse Open Data API.
   - Uses `StationSelector` to get station metadata.
   - Implements retry logic for failed requests.
2. **TRANSFORM**
   - Cleans missing/invalid data and validates data types.
   - Converts units if needed and removes duplicates.
3. **LOAD**
   - Saves data to SQLite database (creates tables if they don't exist).
   - Uses batch inserts for performance and handles duplicate records.

---

## 2. USING THE API

### Starting the API Server
```bash
# Start with auto-reload (development)
uvicorn src.api.main:app --reload

# Start on specific port
uvicorn src.api.main:app --port 8001

# Start with multiple workers (production)
uvicorn src.api.main:app --workers 4 --host 0.0.0.0 --port 8000
```

### Available Endpoints

#### `GET /health`
Check API health and database status.
- **Example**: `curl http://localhost:8000/health`
- **Response**: `{"status": "healthy", "records": 4523, "stations": 44}`

#### `GET /stations`
List all weather stations.
- **Parameters**: `limit` (int), `offset` (int)
- **Example**: `curl "http://localhost:8000/stations?limit=5&offset=0"`

#### `GET /weather/`
Get weather data with filters.
- **Parameters**: `station_id`, `limit`, `offset`, `start_date`, `end_date`
- **Example**: `curl "http://localhost:8000/weather/?station_id=24&limit=10&start_date=2024-01-01"`

#### `GET /weather/statistics/`
Get statistical summary for a station.
- **Parameters**: `station_id`, `start_date`, `end_date`
- **Example**: `curl "http://localhost:8000/weather/statistics/?station_id=24"`

#### `GET /dashboard`
Serve interactive web dashboard.
- **Access**: Open `http://localhost:8000/dashboard` in your browser.

#### `GET /docs`
Interactive API documentation (Swagger UI).
- **Access**: Open `http://localhost:8000/docs` in your browser.

---

## 3. DASHBOARD GUIDE

### Accessing Dashboard
1. Start API server: `uvicorn src.api.main:app --reload`
2. Open browser and navigate to: `http://localhost:8000/dashboard`

### Dashboard Features
- **Station Selector**: Choose from 44 available stations.
- **Date Filtering**: Filter data by selecting Start and End dates.
- **Live Statistics**: View averages, min/max, and totals for temperature, humidity, rain, etc.
- **Interactive Charts**: Hover over data points in Temperature, Humidity, Precipitation, Wind Speed, and Pressure charts.
- **Export Data**: Click the **📥 Exporter CSV** button to download filtered data.
- **Reset**: Click **🔄 Réinitialiser** to clear all filters.

---

## 4. RUNNING TESTS

### Test Commands
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src --cov-report=html
```

### Test Categories
| Category | Description | Count |
| :--- | :--- | :--- |
| `tests/test_api/` | API endpoint tests | 19 |
| `tests/test_extractors/` | Data extraction tests | 12 |
| `tests/test_loaders/` | Database loader tests | 15 |
| `tests/test_structures/` | Data structure tests | 24 |
| **Total** | | **122 tests** |

---

## 5. ADVANCED USAGE

### Docker Commands
```bash
# Build and start services
docker compose build
docker compose up -d

# View logs or stop services
docker compose logs -f
docker compose down
```

### Database Queries
```bash
# Query database directly
sqlite3 database/weather.db
# Example: SELECT AVG(temperature) FROM weather_data WHERE station_id = '24';
```

### Code Quality
```bash
# Format code with black
black src/ --line-length=100

# Run pylint
pylint src/ --disable=C0114,C0115,C0116 --max-line-length=100
```

---

## 6. FAQ

**Q: How many stations are available?**  
A: 44 weather stations across the Toulouse region.

**Q: Is the data real-time?**  
A: Data comes from the Toulouse Open Data API. Updates vary by station.

**Q: Can I export data?**  
A: Yes! Click the "Export CSV" button in the dashboard or query the database directly.

**Q: Can I use PostgreSQL instead of SQLite?**  
A: Yes! Modify `src/loaders/database_loader.py` to use a PostgreSQL connection string.

---

**For more information:**
- [README.md](README.md)
- [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)
- `API_DOCUMENTATION.txt`
- `ARCHITECTURE.txt`
