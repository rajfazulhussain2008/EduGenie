"""
EduGenie Application Entry Point (Epic 3 Alias).
Allows running either `uvicorn main:app` or `uvicorn app:app`.
"""
import os
import uvicorn
from main import app

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app:app", host=host, port=port, reload=True)
