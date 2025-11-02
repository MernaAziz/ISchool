import os
import google.generativeai as genai
from typing import Dict, List
import json

# Global variables for model initialization
_model = None
_genai_configured = False

def _get_model():
    """Lazy initialization of Gemini model"""
    global _model, _genai_configured
    
    if _model is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is not set. "
                "Please create a .env file in the backend directory with: GEMINI_API_KEY=your_key_here"
            )
        
        genai.configure(api_key=api_key)
        _genai_configured = True
        _model = genai.GenerativeModel('gemini-pro')
    
    return _model

async def generate_lesson_title(content: str) -> str:
    """Generate a title for the lesson based on content"""
    try:
        model = _get_model()
        prompt = f"""You are an educational content expert. Generate a concise, descriptive title (maximum 10 words) for the given lesson content.

Lesson content:
{content[:1000]}

Generate a title:"""
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except ValueError as e:
        # Re-raise ValueError (API key missing) with clear message
        raise
    except Exception as e:
        return f"Lesson {hash(content) % 10000}"  # Fallback title

async def generate_explanation(content: str) -> str:
    """Generate an explanation/summary of the lesson"""
    try:
        model = _get_model()
        prompt = f"""You are an educational assistant. Provide a clear, comprehensive explanation of the lesson content in 2-3 paragraphs.

Lesson content:
{content}

Explanation:"""
        
        # Configure generation settings
        generation_config = {
            "temperature": 0.7,
            "max_output_tokens": 500,
        }
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        return response.text.strip()
    except ValueError as e:
        # Re-raise ValueError (API key missing) with clear message
        raise
    except Exception as e:
        return f"Explanation generation failed: {str(e)}. Please review the lesson content manually."

async def generate_quiz(content: str, num_questions: int = 5) -> List[Dict]:
    """Generate multiple choice questions for the lesson"""
    try:
        model = _get_model()
        prompt = f"""You are an educational assessment expert. Generate {num_questions} multiple choice questions based on the lesson content.

Return the response as a JSON array with this exact format:
[
  {{
    "question": "Question text here",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": 0
  }}
]

The correct_answer should be the index (0-3) of the correct option. Return ONLY the JSON array, no other text.

Lesson content:
{content}

Generate {num_questions} MCQs:"""
        
        generation_config = {
            "temperature": 0.7,
            "max_output_tokens": 1000,
        }
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        result = response.text.strip()
        # Try to extract JSON from markdown code blocks if present
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0].strip()
        elif "```" in result:
            result = result.split("```")[1].split("```")[0].strip()
        
        # Remove any leading/trailing text that's not JSON
        start_idx = result.find('[')
        end_idx = result.rfind(']') + 1
        if start_idx != -1 and end_idx > start_idx:
            result = result[start_idx:end_idx]
        
        quiz_data = json.loads(result)
        return quiz_data
    except ValueError as e:
        # Re-raise ValueError (API key missing) with clear message
        raise
    except Exception as e:
        print(f"Error generating quiz: {str(e)}")
        # Return empty quiz on error
        return []

async def answer_question(question: str, context: str) -> str:
    """Answer a question based on lesson context"""
    try:
        model = _get_model()
        prompt = f"""You are an educational assistant. Answer questions based on the provided lesson content. Be clear and concise.

Lesson content:
{context}

Question: {question}

Answer:"""
        
        generation_config = {
            "temperature": 0.7,
            "max_output_tokens": 500,
        }
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        return response.text.strip()
    except ValueError as e:
        # Re-raise ValueError (API key missing) with clear message
        return f"Configuration error: {str(e)}. Please set GEMINI_API_KEY in your .env file."
    except Exception as e:
        return f"I apologize, but I encountered an error while processing your question: {str(e)}"
