from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
import os

from database import get_db, Lesson
from utils.file_processor import process_uploaded_file
from utils.llm_service import generate_lesson_title, generate_explanation, generate_quiz
from utils.vector_db import add_lesson_to_vector_db

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload-lesson")
async def upload_lesson(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a lesson file (PDF or TXT) and generate title, explanation, and quiz"""
    
    # Validate file type
    if not file.content_type in ["application/pdf", "text/plain"]:
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported")
    
    try:
        # Read file contents
        file_contents = await file.read()
        
        # Process file and extract text
        content = await process_uploaded_file(file_contents, file.content_type)
        
        if not content or len(content.strip()) < 50:
            raise HTTPException(status_code=400, detail="File content is too short or empty")
        
        # Generate title, explanation, and quiz using LLM
        title = await generate_lesson_title(content)
        explanation = await generate_explanation(content)
        quiz = await generate_quiz(content, num_questions=5)
        
        # Save lesson to database
        lesson = Lesson(
            title=title,
            filename=file.filename,
            file_type="pdf" if file.content_type == "application/pdf" else "txt",
            content=content,
            explanation=explanation
        )
        db.add(lesson)
        db.commit()
        db.refresh(lesson)
        
        # Add to vector database for semantic search
        add_lesson_to_vector_db(lesson.id, title, content)
        
        # Save file to disk (optional, for future reference)
        file_path = os.path.join(UPLOAD_DIR, f"{lesson.id}_{file.filename}")
        with open(file_path, "wb") as f:
            f.write(file_contents)
        
        return {
            "message": "Lesson uploaded successfully",
            "lesson": lesson.to_dict(),
            "quiz": quiz
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.get("/lessons")
async def list_lessons(db: Session = Depends(get_db)):
    """Get list of all lessons"""
    lessons = db.query(Lesson).all()
    return {
        "lessons": [lesson.to_dict() for lesson in lessons]
    }

@router.get("/lessons/{lesson_id}")
async def get_lesson(lesson_id: int, db: Session = Depends(get_db)):
    """Get a specific lesson with its quiz"""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Regenerate quiz (or you could store it in DB)
    quiz = await generate_quiz(lesson.content, num_questions=5)
    
    lesson_dict = lesson.to_dict()
    lesson_dict["content"] = lesson.content  # Include full content
    
    return {
        "lesson": lesson_dict,
        "quiz": quiz
    }

