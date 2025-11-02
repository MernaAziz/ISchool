import streamlit as st
import os
import asyncio
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add backend directory to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Load environment variables
load_dotenv(backend_path / ".env")

# Import backend modules
from database import init_db, SessionLocal, Lesson
from utils.file_processor import process_uploaded_file
from utils.llm_service import generate_lesson_title, generate_explanation, generate_quiz, answer_question
from utils.vector_db import add_lesson_to_vector_db, search_similar_content

# Helper function to run async functions in Streamlit
def run_async(coro):
    """Run async function in Streamlit"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

# Initialize database
init_db()

# Page configuration
st.set_page_config(
    page_title="AI Learning Assistant",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .lesson-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 1rem 0;
    }
    .quiz-question {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .correct-answer {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

def get_db_session():
    """Get database session"""
    return SessionLocal()

# Initialize session state
if 'lessons' not in st.session_state:
    st.session_state.lessons = []
if 'selected_lesson' not in st.session_state:
    st.session_state.selected_lesson = None

# Header
st.markdown('<div class="main-header">📚 AI Learning Assistant</div>', unsafe_allow_html=True)

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Choose a page", ["🏠 Home", "👨‍🏫 Teacher Portal", "👨‍🎓 Student Portal"])

# Load lessons from database
def load_lessons():
    db = get_db_session()
    try:
        lessons = db.query(Lesson).all()
        return [lesson.to_dict() for lesson in lessons]
    finally:
        db.close()

# Home Page
if page == "🏠 Home":
    st.header("Welcome to AI Learning Assistant")
    st.markdown("""
    ### Features:
    
    **For Teachers:**
    - 📤 Upload lesson files (PDF or TXT)
    - 🤖 Automatic generation of:
      - Lesson title
      - Comprehensive explanation
      - Quiz with 5 Multiple Choice Questions
    
    **For Students:**
    - 📚 Browse available lessons
    - 🔍 Semantic search for lessons
    - 💬 Ask questions about lessons with AI-powered answers
    
    ---
    
    ### Getting Started:
    1. Navigate to **Teacher Portal** to upload your first lesson
    2. Go to **Student Portal** to explore lessons and ask questions
    """)
    
    # Show API key status
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        st.success("✅ Gemini API key is configured")
    else:
        st.error("⚠️ Gemini API key not found. Please set GEMINI_API_KEY in your .env file")

# Teacher Portal
elif page == "👨‍🏫 Teacher Portal":
    st.header("👨‍🏫 Teacher Portal")
    st.markdown("Upload lesson files and generate educational content automatically")
    
    tab1, tab2 = st.tabs(["📤 Upload Lesson", "📋 My Lessons"])
    
    with tab1:
        st.subheader("Upload a Lesson")
        
        uploaded_file = st.file_uploader(
            "Choose a PDF or TXT file",
            type=['pdf', 'txt'],
            help="Upload your lesson file"
        )
        
        if uploaded_file is not None:
            st.info(f"📄 File: {uploaded_file.name} ({uploaded_file.size} bytes)")
            
            if st.button("🚀 Upload & Generate Content", type="primary"):
                with st.spinner("Processing your file and generating content..."):
                    try:
                        # Read file contents
                        file_contents = uploaded_file.read()
                        file_type = uploaded_file.type
                        
                        # Process file
                        content = run_async(process_uploaded_file(file_contents, file_type))
                        
                        if not content or len(content.strip()) < 50:
                            st.error("File content is too short or empty. Please upload a valid lesson file.")
                        else:
                            # Generate content
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            status_text.text("Generating title...")
                            progress_bar.progress(20)
                            title = run_async(generate_lesson_title(content))
                            
                            status_text.text("Generating explanation...")
                            progress_bar.progress(40)
                            explanation = run_async(generate_explanation(content))
                            
                            status_text.text("Generating quiz...")
                            progress_bar.progress(60)
                            quiz = run_async(generate_quiz(content, num_questions=5))
                            
                            # Save to database
                            status_text.text("Saving to database...")
                            progress_bar.progress(80)
                            db = get_db_session()
                            try:
                                lesson = Lesson(
                                    title=title,
                                    filename=uploaded_file.name,
                                    file_type="pdf" if file_type == "application/pdf" else "txt",
                                    content=content,
                                    explanation=explanation
                                )
                                db.add(lesson)
                                db.commit()
                                db.refresh(lesson)
                                
                                # Add to vector database
                                add_lesson_to_vector_db(lesson.id, title, content)
                                
                                progress_bar.progress(100)
                                status_text.text("Complete!")
                                
                                st.success(f"✅ Lesson '{title}' uploaded successfully!")
                                
                                # Display results
                                st.subheader("Generated Content")
                                
                                st.markdown("### 📝 Title")
                                st.write(title)
                                
                                st.markdown("### 📖 Explanation")
                                st.write(explanation)
                                
                                st.markdown("### 📝 Quiz (5 MCQs)")
                                if quiz and len(quiz) > 0:
                                    for idx, q in enumerate(quiz, 1):
                                        if isinstance(q, dict) and 'question' in q:
                                            with st.container():
                                                st.markdown(f"**Question {idx}:** {q['question']}")
                                                if 'options' in q and isinstance(q['options'], list):
                                                    options = q['options']
                                                    correct_idx = q.get('correct_answer', -1)
                                                    
                                                    for opt_idx, option in enumerate(options):
                                                        prefix = "✅" if opt_idx == correct_idx else "⚪"
                                                        st.markdown(f"{prefix} {chr(65 + opt_idx)}. {option}")
                                                st.divider()
                                else:
                                    st.warning("⚠️ Quiz generation failed or was blocked by safety filters. The lesson was saved, but no quiz could be generated.")
                                
                            except Exception as e:
                                db.rollback()
                                st.error(f"Error saving lesson: {str(e)}")
                            finally:
                                db.close()
                        
                    except ValueError as e:
                        st.error(f"Error processing file: {str(e)}")
                    except Exception as e:
                        st.error(f"Error generating content: {str(e)}")
    
    with tab2:
        st.subheader("My Lessons")
        
        if st.button("🔄 Refresh"):
            st.rerun()
        
        lessons = load_lessons()
        
        if not lessons:
            st.info("No lessons uploaded yet. Upload your first lesson in the 'Upload Lesson' tab!")
        else:
            for lesson in lessons:
                with st.expander(f"📚 {lesson['title']} - {lesson['filename']}"):
                    st.write(f"**Uploaded:** {lesson['created_at']}")
                    st.write(f"**Type:** {lesson['file_type'].upper()}")
                    
                    if lesson['explanation']:
                        st.markdown("**Explanation:**")
                        st.write(lesson['explanation'])
                    
                    # Use different key for button to avoid conflict with session state
                    quiz_key = f"quiz_data_{lesson['id']}"
                    button_key = f"btn_quiz_{lesson['id']}"
                    
                    if st.button(f"View Quiz", key=button_key):
                        with st.spinner("Generating quiz..."):
                            db = get_db_session()
                            try:
                                lesson_obj = db.query(Lesson).filter(Lesson.id == lesson['id']).first()
                                if lesson_obj:
                                    quiz = run_async(generate_quiz(lesson_obj.content, num_questions=5))
                                    st.session_state[quiz_key] = quiz
                                    st.rerun()
                            finally:
                                db.close()
                    
                    # Display quiz if it exists in session state
                    if quiz_key in st.session_state:
                        quiz = st.session_state[quiz_key]
                        if quiz and len(quiz) > 0:
                            st.markdown("### Quiz Questions")
                            for idx, q in enumerate(quiz, 1):
                                if isinstance(q, dict) and 'question' in q:
                                    st.markdown(f"**{idx}. {q['question']}**")
                                    if 'options' in q and isinstance(q['options'], list):
                                        for opt_idx, option in enumerate(q['options']):
                                            prefix = "✅" if opt_idx == q.get('correct_answer', -1) else "  "
                                            st.markdown(f"{prefix} {chr(65 + opt_idx)}. {option}")
                                    st.divider()
                        else:
                            st.warning("⚠️ Quiz generation failed or was blocked. This may happen if the content triggers safety filters. Please try uploading the lesson again or modify the content.")

# Student Portal
elif page == "👨‍🎓 Student Portal":
    st.header("👨‍🎓 Student Portal")
    st.markdown("Browse lessons and ask questions")
    
    lessons = load_lessons()
    
    if not lessons:
        st.info("No lessons available. Ask your teacher to upload some lessons!")
    else:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("📚 Available Lessons")
            
            # Search functionality
            search_query = st.text_input("🔍 Search lessons", placeholder="Type to search...")
            
            # Filter lessons based on search
            if search_query:
                try:
                    similar_content = search_similar_content(search_query, lesson_id=None, top_k=5)
                    lesson_ids = set()
                    for chunk in similar_content:
                        if "lesson_id" in chunk.get("metadata", {}):
                            lesson_ids.add(chunk["metadata"]["lesson_id"])
                    
                    filtered_lessons = [l for l in lessons if l['id'] in lesson_ids]
                    if not filtered_lessons:
                        st.info("No matching lessons found")
                        display_lessons = lessons
                    else:
                        display_lessons = filtered_lessons
                except:
                    display_lessons = lessons
            else:
                display_lessons = lessons
            
            # Lesson selection
            lesson_options = {f"{l['title']}": l['id'] for l in display_lessons}
            selected_title = st.selectbox("Select a lesson", options=list(lesson_options.keys()))
            selected_lesson_id = lesson_options[selected_title]
            
            # Get selected lesson details
            selected_lesson = next(l for l in lessons if l['id'] == selected_lesson_id)
        
        with col2:
            st.subheader(f"📖 {selected_lesson['title']}")
            
            if selected_lesson['explanation']:
                st.markdown("**Overview:**")
                st.write(selected_lesson['explanation'])
            
            st.divider()
            
            # Q&A Section
            st.markdown("### 💬 Ask a Question")
            question = st.text_area(
                "Enter your question about this lesson:",
                placeholder="e.g., Can you explain the main concept?",
                height=100
            )
            
            if st.button("🔍 Ask Question", type="primary"):
                if question.strip():
                    with st.spinner("Thinking..."):
                        try:
                            db = get_db_session()
                            try:
                                lesson_obj = db.query(Lesson).filter(Lesson.id == selected_lesson_id).first()
                                if lesson_obj:
                                    # Search for relevant context
                                    similar_content = search_similar_content(
                                        question, 
                                        lesson_id=selected_lesson_id, 
                                        top_k=3
                                    )
                                    
                                    # Combine relevant chunks
                                    context_parts = [chunk["content"] for chunk in similar_content]
                                    context = "\n\n".join(context_parts)
                                    
                                    if not context or len(context) < 100:
                                        context = lesson_obj.content
                                    
                                    # Generate answer
                                    answer = run_async(answer_question(question, context))
                                    
                                    st.markdown("### 💡 Answer")
                                    st.success(answer)
                                    
                                    if similar_content:
                                        with st.expander("📎 Relevant Sections"):
                                            for chunk in similar_content[:2]:
                                                st.markdown(f"*{chunk['content'][:200]}...*")
                            finally:
                                db.close()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                else:
                    st.warning("Please enter a question")

