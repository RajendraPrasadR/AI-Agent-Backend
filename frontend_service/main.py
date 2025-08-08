from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import os

app = FastAPI(title="AI Agent Frontend Service", version="1.0.0")

# Setup templates and static files
templates = Jinja2Templates(directory="templates")

# Create templates directory if it doesn't exist
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except RuntimeError:
    # Directory might not exist yet
    pass

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "message": "Hello, I'm Frontend Service",
        "service": "frontend_service"
    })

@app.get("/api/status")
def get_status():
    return {
        "message": "Hello, I'm Frontend Service",
        "service": "frontend_service",
        "status": "running",
        "features": [
            "Task management UI",
            "Status monitoring",
            "Result display"
        ]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "frontend"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
