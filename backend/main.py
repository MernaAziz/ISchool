from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
from dotenv import load_dotenv
import uvicorn

from routes import teachers, students
from database import init_db

load_dotenv()

app = FastAPI(title="AI Learning Assistant", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Include routers
app.include_router(teachers.router, prefix="/api/teachers", tags=["teachers"])
app.include_router(students.router, prefix="/api/students", tags=["students"])

@app.get("/")
async def root():
    return {"message": "AI Learning Assistant API"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

