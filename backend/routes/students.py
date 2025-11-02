from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import get_db, Lesson
from utils.vector_db import search_similar_content
from utils.llm_service import answer_question

router = APIRouter()

class QuestionRequest(BaseModel):
    lesson_id: int
    question: str

@router.get("/lessons")
async def list_lessons(db: Session = Depends(get_db)):
    """Get list of all available lessons"""
    lessons = db.query(Lesson).all()
    return {
        "lessons": [lesson.to_dict() for lesson in lessons]
    }

@router.get("/lessons/{lesson_id}")
async def get_lesson(lesson_id: int, db: Session = Depends(get_db)):
    """Get lesson details"""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    lesson_dict = lesson.to_dict()
    # Don't include full content in list view for performance
    return {"lesson": lesson_dict}

@router.post("/ask-question")
async def ask_question(request: QuestionRequest, db: Session = Depends(get_db)):
    """Ask a question about a specific lesson"""
    # Get lesson from database
    lesson = db.query(Lesson).filter(Lesson.id == request.lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Search for relevant context in vector database
    similar_content = search_similar_content(request.question, lesson_id=request.lesson_id, top_k=3)
    
    # Combine relevant chunks with full lesson content for context
    context_parts = [chunk["content"] for chunk in similar_content]
    context = "\n\n".join(context_parts)
    
    # If no specific chunks found, use full lesson content
    if not context or len(context) < 100:
        context = lesson.content
    
    # Generate answer using LLM
    answer = await answer_question(request.question, context)
    
    return {
        "question": request.question,
        "answer": answer,
        "lesson_title": lesson.title,
        "relevant_sections": [chunk["content"][:200] + "..." for chunk in similar_content[:2]]
    }

@router.get("/search-lessons")
async def search_lessons(query: str, db: Session = Depends(get_db)):
    """Search for lessons using semantic search"""
    # Search in vector database
    similar_content = search_similar_content(query, lesson_id=None, top_k=5)
    
    # Get unique lesson IDs
    lesson_ids = set()
    for chunk in similar_content:
        if "lesson_id" in chunk["metadata"]:
            lesson_ids.add(chunk["metadata"]["lesson_id"])
    
    # Fetch lessons from database
    lessons = db.query(Lesson).filter(Lesson.id.in_(lesson_ids)).all() if lesson_ids else []
    
    return {
        "query": query,
        "lessons": [lesson.to_dict() for lesson in lessons]
    }

