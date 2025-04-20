"""
FastAPI app scaffold for agent and spectator endpoints.
"""
from fastapi import FastAPI

app = FastAPI()

@app.get("/healthz")
def healthz():
    """Health check endpoint."""
    return {"status": "ok"}
