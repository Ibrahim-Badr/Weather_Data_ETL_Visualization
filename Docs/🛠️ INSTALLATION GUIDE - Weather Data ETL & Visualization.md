# 🛠️ INSTALLATION GUIDE - Weather Data ETL & Visualization

---

## 📋 TABLE OF CONTENTS

1. [Prerequisites](#1-prerequisites)
2. [Local Installation (Windows)](#2-local-installation-windows)
3. [Local Installation (Linux/Mac)](#3-local-installation-linuxmac)
4. [Docker Installation](#4-docker-installation)
5. [Verification Steps](#5-verification-steps)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. PREREQUISITES

### Required Software
- **Python 3.11** or higher
- **pip** (Python package manager)
- **Git**
- **Docker & Docker Compose** (optional, for containerized deployment)

### System Requirements
- **OS**: Windows 10/11, Ubuntu 20.04+, macOS 11+
- **RAM**: 2 GB minimum, 4 GB recommended
- **Disk Space**: 500 MB
- **Internet**: Required for data extraction

### Check Installations
```bash
# Check Python version
python --version
# Expected output: Python 3.11.x or higher

# Check pip
pip --version

# Check Git
git --version

# Check Docker (optional)
docker --version
docker compose version
```

---

## 2. LOCAL INSTALLATION (WINDOWS)

### STEP 1: Clone Repository
```powershell
git clone https://github.com/YOUR_USERNAME/Weather_Data_ETL_Visualization.git
cd Weather_Data_ETL_Visualization
```

### STEP 2: Create Virtual Environment
```powershell
# Create venv
python -m venv venv

# Activate venv
venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

### STEP 3: Install Dependencies
```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install all packages
pip install -r requirements.txt
```
> **Note**: This will install `requests`, `pandas`, `sqlalchemy`, `fastapi`, `uvicorn`, `pytest`, and others.

### STEP 4: Create Database Directory
```powershell
mkdir database
```

### STEP 5: Run Initial ETL
```powershell
# Extract data for 2 stations (faster for testing)
python main.py --stations 24 25 --limit 100
```
**Expected output:**
- ✓ Extracted 200 records from API
- ✓ Transformed 200 records
- ✓ Saved 200 records to database
- ✓ ETL pipeline completed successfully

### STEP 6: Start API Server
```powershell
uvicorn src.api.main:app --reload

# Server will start at: http://localhost:8000
# Open browser and go to:
# - Dashboard: http://localhost:8000/dashboard
# - API Docs: http://localhost:8000/docs
```

---

## 3. LOCAL INSTALLATION (LINUX/MAC)

### STEP 1: Clone Repository
```bash
git clone https://github.com/Ibrahim-Badr/Weather_Data_ETL_Visualization
cd Weather_Data_ETL_Visualization
```

### STEP 2: Create Virtual Environment
```bash
# Create venv
python3 -m venv venv

# Activate venv
source venv/bin/activate

# You should see (venv) in your terminal prompt
```

### STEP 3: Install Dependencies
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install packages
pip install -r requirements.txt
```

### STEP 4: Create Database Directory
```bash
mkdir -p database
```

### STEP 5: Run Initial ETL
```bash
python main.py --stations 24 25 --limit 100
```

### STEP 6: Start API Server
```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 4. DOCKER INSTALLATION

### STEP 1: Clone Repository
```bash
git clone https://github.com/Ibrahim-Badr/Weather_Data_ETL_Visualization
cd Weather_Data_ETL_Visualization
```

### STEP 2: Build Docker Images
```bash
# Windows PowerShell / Linux / Mac
docker compose build
```
> **Note**: This process downloads the Python 3.11 base image, installs dependencies, and copies code. Takes 3-5 minutes on first run.

### STEP 3: Start Services
```bash
# Start in background
docker compose up -d

# Start with logs (foreground)
docker compose up
```
**Services initialized:**
- `weather-database` (Alpine container)
- `weather-etl` (runs ETL pipeline)
- `weather-api` (FastAPI server on port 8000)

### STEP 4: Check Status
```bash
# Check running services
docker compose ps

# View logs
docker compose logs -f
```

### STEP 5: Access Application
- **Dashboard**: http://localhost:8000/dashboard
- **API Docs**:  http://localhost:8000/docs
- **Health**:    http://localhost:8000/health

### STEP 6: Stop Services
```bash
# Stop services
docker compose down

# Stop and remove database
docker compose down -v
```

---

## 5. VERIFICATION STEPS

### Test 1: Check Database
```bash
# Windows
dir database

# Linux/Mac
ls -lh database/
```
**Expected**: `weather.db` file should exist (~1-5 MB).

### Test 2: Test API Health
```bash
# Windows PowerShell
Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing

# Linux/Mac
curl http://localhost:8000/health
```
**Expected output**: `{"status":"healthy","records":200,"stations":2}`

### Test 3: Run Unit Tests
```bash
# Activate venv first (if not already)
pytest --cov=src -v
```
**Expected output**: `122 passed`, `Coverage: 85%`.

### Test 4: Test Dashboard
1. Open http://localhost:8000/dashboard
2. Select a station from dropdown
3. Verify charts are displayed
4. Try date filters
5. Click "Export CSV" button

---

## 6. TROUBLESHOOTING

| Problem | Solution |
| :--- | :--- |
| **Port 8000 already in use** | Find process using port 8000 and kill it, or use `uvicorn src.api.main:app --port 8001` |
| **Module not found error** | Ensure venv is activated and run `pip install -r requirements.txt --force-reinstall` |
| **ETL fails with timeout** | Reduce limit/stations: `python main.py --stations 24 --limit 50`. Check internet. |
| **Docker container won't start** | Check logs: `docker compose logs api`. Rebuild: `docker compose build --no-cache`. |
| **Tests fail** | Ensure database exists by running ETL first. Check specific test: `pytest tests/test_api/test_health.py -v` |
| **Dashboard not loading** | Check API health. Check browser console (F12). Clear cache or try another browser. |

---

## NEXT STEPS

✅ **Installation complete!**

Now you can:
1. **Run ETL pipeline**: `python main.py --list-stations`
2. **Start API**: `uvicorn src.api.main:app --reload`
3. **Open dashboard**: http://localhost:8000/dashboard
4. **Run tests**: `pytest --cov=src`
5. Read `USER_GUIDE.md` for detailed usage

---

**For more help, see:**
- [README.md](README.md)
- `USER_GUIDE.txt`
- `API_DOCUMENTATION.txt`
