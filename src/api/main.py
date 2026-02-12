"""
FastAPI Weather Data API - Main Application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .routes import stations, weather

# Create FastAPI app
app = FastAPI(
    title="Weather Data ETL API",
    description="REST API for Toulouse weather data (4,500+ records from 44 stations)",
    version="1.0.0"
)

# Add CORS middleware for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = Path(__file__).parent.parent.parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Include routers
app.include_router(stations.router)
app.include_router(weather.router)


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Interactive weather dashboard."""
    dashboard_file = Path(__file__).parent.parent.parent / "static" / "index.html"
    if dashboard_file.exists():
        return FileResponse(dashboard_file)
    return HTMLResponse("<h1>Dashboard not found</h1>", status_code=404)


@app.get("/", response_class=HTMLResponse)
async def root():
    """API homepage."""
    return """
    <html>
        <head>
            <title>Weather Data ETL API</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 40px; }
                h1 { color: #2c3e50; }
                .endpoint { background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 8px; }
                code { background: #e9ecef; padding: 2px 6px; border-radius: 4px; font-family: monospace; }
                a { color: #3498db; text-decoration: none; }
                .dashboard-btn { 
                    display: inline-block;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 15px 30px;
                    border-radius: 8px;
                    font-weight: bold;
                    margin: 20px 0;
                    text-decoration: none;
                }
                .dashboard-btn:hover { opacity: 0.9; }
            </style>
        </head>
        <body>
            <h1>🌤️ Weather Data ETL API</h1>
            <p><strong>4,523 weather records from 44 Toulouse stations</strong></p>
            
            <a href="/dashboard" class="dashboard-btn">🎨 Open Interactive Dashboard →</a>
            
            <div class="endpoint">
                <h3>📋 Stations</h3>
                <p><code>GET /stations</code> - List all stations<br>
                <code>GET /stations/24</code> - Station details<br>
                <code>GET /stations?location=Toulouse&limit=10</code> - Filtered</p>
            </div>
            
            <div class="endpoint">
                <h3>🌡️ Weather Data</h3>
                <p><code>GET /weather?station_id=24&limit=50</code> - Weather records<br>
                <code>GET /weather/stats</code> - Statistics<br>
                <code>GET /weather?station_id=24&min_temp=15&max_temp=25</code> - Filtered</p>
            </div>
            
            <h3>📖 Interactive API Docs</h3>
            <p><a href="/docs">Swagger UI → /docs</a> | <a href="/redoc">ReDoc → /redoc</a></p>
            
            <hr>
            <p><em>Powered by FastAPI + SQLite + Toulouse Open Data</em></p>
        </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "records": 4523, "stations": 44}
