#!/usr/bin/env python3
"""
Simple test script to verify FastAPI server functionality
"""
import uvicorn
from fastapi import FastAPI

# Create a simple test app
app = FastAPI(title="video2music Test", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "🎵 video2music backend is running!", "status": "ok"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "video2music"}

if __name__ == "__main__":
    print("🎵 Starting video2music test server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📍 API docs will be available at: http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop the server")
    
    uvicorn.run(
        "test_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 