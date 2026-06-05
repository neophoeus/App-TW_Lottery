import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from core.predictor import LotteryPredictor, RULES

app = FastAPI(title="TW Lottery API", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "TW Lottery API is running 🚀"}

@app.get("/api/games")
def get_games():
    """Return supported games"""
    return [
        {"key": k, "name": v['name']} 
        for k, v in RULES.items()
    ]

@app.get("/api/predict/{game_key}")
def predict(game_key: str):
    """Run prediction for specific game"""
    if game_key not in RULES:
        raise HTTPException(status_code=404, detail="Game not found")
        
    predictor = LotteryPredictor(game_key)
    try:
        # Load data returns (success, msg)
        success, msg = predictor.load_data()
        if not success:
             raise HTTPException(status_code=500, detail=msg)
             
        # Run all strategies
        results = predictor.run_all()
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/update")
def update_data():
    """Trigger data update from lotto-8.com"""
    from core.fetcher import LottoFetcher
    fetcher = LottoFetcher()
    try:
        results = fetcher.fetch_all()
        return {"status": "success", "details": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve static files from the 'static' directory if it exists
static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(static_path):
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    import sys
    import webbrowser
    import threading
    import time

    # Detect if we should run in reload mode (typically for development)
    is_reload = "--reload" in sys.argv or "reload" in sys.argv
    
    # Automatically open local server URL in browser for portable users
    if not is_reload:
        def open_browser():
            time.sleep(1.5)  # Wait for uvicorn server to bind to port
            webbrowser.open("http://localhost:8000")
        threading.Thread(target=open_browser, daemon=True).start()

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=is_reload)
