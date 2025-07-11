#!/usr/bin/env python3
"""
Script to start the FastAPI server
"""

import subprocess
import sys
import os

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting FastAPI server...")
    print("=" * 50)
    
    try:
        # Check if uvicorn is available
        try:
            import uvicorn
            print("✅ Uvicorn is available")
        except ImportError:
            print("❌ Uvicorn not found. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "uvicorn"])
            print("✅ Uvicorn installed successfully")
        
        # Start the server
        print("🔄 Starting server on http://localhost:8000")
        print("📋 API Documentation: http://localhost:8000/docs")
        print("🛑 Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Start uvicorn
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    start_server() 