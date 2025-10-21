#!/usr/bin/env python3
import uvicorn
import os

if __name__ == "__main__":
    print("=" * 50)
    print("      Swastik Assayers Server")
    print("=" * 50)
    print("\nStarting server on http://localhost:5000")
    print("API Documentation: http://localhost:5000/docs")
    print("\nPress Ctrl+C to stop the server")
    print("-" * 50)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info"
    )