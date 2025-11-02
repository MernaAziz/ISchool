# AI Learning Assistant - Streamlit Version

A simplified single-file Streamlit application that combines frontend and backend functionality.

## Features

### For Teachers:
- 📤 Upload lesson files (PDF or TXT)
- 🤖 Automatic generation of:
  - Lesson title
  - Comprehensive explanation
  - Quiz with 5 Multiple Choice Questions (MCQs)

### For Students:
- 📚 Browse available lessons
- 🔍 Semantic search for lessons
- 💬 Ask questions about lessons with AI-powered answers

## Quick Start

### 1. Install Dependencies

```powershell
pip install -r streamlit_requirements.txt
```

Or install the full requirements:
```powershell
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the `backend` directory:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

Get your API key from: https://makersuite.google.com/app/apikey

### 3. Run the Streamlit App

```powershell
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

### Teacher Workflow:
1. Click on **👨‍🏫 Teacher Portal** in the sidebar
2. Go to **📤 Upload Lesson** tab
3. Upload a PDF or TXT file
4. Click **🚀 Upload & Generate Content**
5. View the generated title, explanation, and quiz
6. Go to **📋 My Lessons** to see all uploaded lessons

### Student Workflow:
1. Click on **👨‍🎓 Student Portal** in the sidebar
2. Browse available lessons from the left panel
3. Use the search box to find relevant lessons
4. Select a lesson to view its overview
5. Type your question in the text area
6. Click **🔍 Ask Question** to get AI-powered answers

## File Structure

```
.
├── streamlit_app.py           # Main Streamlit application
├── backend/                   # Backend modules
│   ├── database.py           # Database models
│   ├── utils/
│   │   ├── file_processor.py # PDF/TXT processing
│   │   ├── llm_service.py    # Gemini AI integration
│   │   └── vector_db.py      # ChromaDB vector database
│   └── .env                  # Environment variables
├── streamlit_requirements.txt # Minimal requirements for Streamlit
└── requirements.txt          # Full requirements (includes FastAPI)

```

## Advantages of Streamlit Version

✅ **Single File**: Everything in one `streamlit_app.py` file
✅ **No Node.js Required**: Pure Python application
✅ **Easy Deployment**: Can be deployed to Streamlit Cloud
✅ **Simple Interface**: Clean, modern UI without complex setup
✅ **Interactive**: Built-in widgets and components

## Notes

- The database (`lessons.db`) is stored in the project root
- Vector database (ChromaDB) is stored in `./chroma_db`
- All uploaded files are processed and stored in the database
- The app uses the same backend modules as the FastAPI version

## Troubleshooting

### If you get "GEMINI_API_KEY not found":
- Make sure you created a `.env` file in the `backend` directory
- Verify the file contains: `GEMINI_API_KEY=your_key_here`
- Restart the Streamlit app

### If ChromaDB errors occur:
- The app will automatically create the `chroma_db` directory
- Make sure you have write permissions in the project directory

## Deploy to Streamlit Cloud

1. Push your code to GitHub
2. Go to https://share.streamlit.io
3. Connect your repository
4. Set environment variable `GEMINI_API_KEY` in Streamlit Cloud settings
5. Deploy!

