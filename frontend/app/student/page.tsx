'use client'

import { useState, useEffect } from 'react'
import axios from 'axios'

const API_URL = 'http://localhost:8000'

interface Lesson {
    id: number
    title: string
    filename: string
    file_type: string
    explanation: string
    created_at: string
}

interface QuestionResponse {
    question: string
    answer: string
    lesson_title: string
    relevant_sections: string[]
}

export default function StudentPage() {
    const [lessons, setLessons] = useState<Lesson[]>([])
    const [selectedLesson, setSelectedLesson] = useState<Lesson | null>(null)
    const [question, setQuestion] = useState('')
    const [loading, setLoading] = useState(false)
    const [answer, setAnswer] = useState<QuestionResponse | null>(null)
    const [searchQuery, setSearchQuery] = useState('')

    useEffect(() => {
        loadLessons()
    }, [])

    const loadLessons = async () => {
        try {
            const response = await axios.get(`${API_URL}/api/students/lessons`)
            setLessons(response.data.lessons)
        } catch (error: any) {
            console.error('Error loading lessons:', error)
            alert('Error loading lessons. Make sure the backend server is running.')
        }
    }

    const loadLessonDetails = async (lessonId: number) => {
        try {
            const response = await axios.get(`${API_URL}/api/students/lessons/${lessonId}`)
            setSelectedLesson(response.data.lesson)
            setAnswer(null)
            setQuestion('')
        } catch (error: any) {
            alert(`Error loading lesson: ${error.response?.data?.detail || error.message}`)
        }
    }

    const handleAskQuestion = async () => {
        if (!selectedLesson || !question.trim()) {
            alert('Please select a lesson and enter a question')
            return
        }

        setLoading(true)
        try {
            const response = await axios.post(`${API_URL}/api/students/ask-question`, {
                lesson_id: selectedLesson.id,
                question: question.trim(),
            })
            setAnswer(response.data)
        } catch (error: any) {
            alert(`Error: ${error.response?.data?.detail || error.message}`)
        } finally {
            setLoading(false)
        }
    }

    const handleSearch = async () => {
        if (!searchQuery.trim()) {
            loadLessons()
            return
        }

        try {
            const response = await axios.get(`${API_URL}/api/students/search-lessons`, {
                params: { query: searchQuery },
            })
            setLessons(response.data.lessons)
        } catch (error: any) {
            console.error('Error searching:', error)
        }
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 py-8">
            <div className="container mx-auto px-4 max-w-6xl">
                <div className="mb-8">
                    <a href="/" className="text-green-600 hover:text-green-700 mb-4 inline-block">
                        ← Back to Home
                    </a>
                    <h1 className="text-4xl font-bold text-gray-800">Student Portal</h1>
                    <p className="text-gray-600 mt-2">Browse lessons and ask questions</p>
                </div>

                <div className="grid md:grid-cols-3 gap-8">
                    {/* Lessons List */}
                    <div className="bg-white rounded-xl shadow-lg p-6">
                        <div className="mb-4">
                            <div className="flex gap-2 mb-4">
                                <input
                                    type="text"
                                    placeholder="Search lessons..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                                    className="flex-1 px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                                />
                                <button
                                    onClick={handleSearch}
                                    className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
                                >
                                    Search
                                </button>
                            </div>
                            <button
                                onClick={loadLessons}
                                className="text-green-600 hover:text-green-700 text-sm"
                            >
                                Show All
                            </button>
                        </div>
                        <h2 className="text-xl font-semibold mb-4">Available Lessons</h2>
                        <div className="space-y-2 max-h-96 overflow-y-auto">
                            {lessons.length === 0 ? (
                                <p className="text-gray-500 text-center py-8">No lessons available</p>
                            ) : (
                                lessons.map((lesson) => (
                                    <div
                                        key={lesson.id}
                                        onClick={() => loadLessonDetails(lesson.id)}
                                        className={`p-3 border rounded-lg cursor-pointer transition-colors ${selectedLesson?.id === lesson.id
                                                ? 'bg-green-50 border-green-300'
                                                : 'hover:bg-gray-50'
                                            }`}
                                    >
                                        <h3 className="font-semibold text-gray-800">{lesson.title}</h3>
                                        <p className="text-xs text-gray-400 mt-1">
                                            {new Date(lesson.created_at).toLocaleDateString()}
                                        </p>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>

                    {/* Selected Lesson & Q&A */}
                    <div className="md:col-span-2 space-y-6">
                        {selectedLesson ? (
                            <>
                                {/* Lesson Info */}
                                <div className="bg-white rounded-xl shadow-lg p-6">
                                    <h2 className="text-2xl font-semibold mb-2">{selectedLesson.title}</h2>
                                    {selectedLesson.explanation && (
                                        <div className="mt-4">
                                            <h3 className="text-lg font-semibold mb-2">Overview</h3>
                                            <p className="text-gray-700 whitespace-pre-wrap">
                                                {selectedLesson.explanation}
                                            </p>
                                        </div>
                                    )}
                                </div>

                                {/* Q&A Section */}
                                <div className="bg-white rounded-xl shadow-lg p-6">
                                    <h2 className="text-xl font-semibold mb-4">Ask a Question</h2>
                                    <div className="space-y-4">
                                        <textarea
                                            value={question}
                                            onChange={(e) => setQuestion(e.target.value)}
                                            placeholder="Type your question about this lesson..."
                                            className="w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 resize-none"
                                            rows={3}
                                            onKeyPress={(e) => {
                                                if (e.key === 'Enter' && e.ctrlKey) {
                                                    handleAskQuestion()
                                                }
                                            }}
                                        />
                                        <button
                                            onClick={handleAskQuestion}
                                            disabled={loading || !question.trim()}
                                            className="w-full bg-green-600 text-white py-3 px-4 rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                                        >
                                            {loading ? 'Getting answer...' : 'Ask Question (Ctrl+Enter)'}
                                        </button>

                                        {answer && (
                                            <div className="mt-6 p-4 bg-green-50 rounded-lg border border-green-200">
                                                <div className="flex items-start gap-3">
                                                    <div className="flex-shrink-0 w-8 h-8 bg-green-500 rounded-full flex items-center justify-center text-white font-bold">
                                                        Q
                                                    </div>
                                                    <div className="flex-1">
                                                        <p className="font-semibold text-gray-800 mb-2">{answer.question}</p>
                                                    </div>
                                                </div>
                                                <div className="flex items-start gap-3 mt-4">
                                                    <div className="flex-shrink-0 w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold">
                                                        A
                                                    </div>
                                                    <div className="flex-1">
                                                        <p className="text-gray-700 whitespace-pre-wrap">{answer.answer}</p>
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </>
                        ) : (
                            <div className="bg-white rounded-xl shadow-lg p-12 text-center">
                                <svg
                                    className="w-16 h-16 text-gray-400 mx-auto mb-4"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                                    />
                                </svg>
                                <p className="text-gray-500 text-lg">
                                    Select a lesson from the list to start asking questions
                                </p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}

