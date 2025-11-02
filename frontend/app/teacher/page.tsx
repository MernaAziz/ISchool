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

interface QuizItem {
    question: string
    options: string[]
    correct_answer: number
}

export default function TeacherPage() {
    const [file, setFile] = useState<File | null>(null)
    const [uploading, setUploading] = useState(false)
    const [lessons, setLessons] = useState<Lesson[]>([])
    const [selectedLesson, setSelectedLesson] = useState<Lesson | null>(null)
    const [quiz, setQuiz] = useState<QuizItem[]>([])

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0])
        }
    }

    const handleUpload = async () => {
        if (!file) {
            alert('Please select a file')
            return
        }

        setUploading(true)
        const formData = new FormData()
        formData.append('file', file)

        try {
            const response = await axios.post(`${API_URL}/api/teachers/upload-lesson`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            })

            alert('Lesson uploaded successfully!')
            setFile(null)
            loadLessons()
            // Reset file input
            const fileInput = document.getElementById('file-input') as HTMLInputElement
            if (fileInput) fileInput.value = ''
        } catch (error: any) {
            alert(`Error: ${error.response?.data?.detail || error.message}`)
        } finally {
            setUploading(false)
        }
    }

    const loadLessons = async () => {
        try {
            const response = await axios.get(`${API_URL}/api/teachers/lessons`)
            setLessons(response.data.lessons)
        } catch (error: any) {
            console.error('Error loading lessons:', error)
        }
    }

    const loadLessonDetails = async (lessonId: number) => {
        try {
            const response = await axios.get(`${API_URL}/api/teachers/lessons/${lessonId}`)
            setSelectedLesson(response.data.lesson)
            setQuiz(response.data.quiz)
        } catch (error: any) {
            alert(`Error loading lesson: ${error.response?.data?.detail || error.message}`)
        }
    }

    // Load lessons on mount
    useEffect(() => {
        loadLessons()
    }, [])

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
            <div className="container mx-auto px-4 max-w-6xl">
                <div className="mb-8">
                    <a href="/" className="text-primary-600 hover:text-primary-700 mb-4 inline-block">
                        ← Back to Home
                    </a>
                    <h1 className="text-4xl font-bold text-gray-800">Teacher Portal</h1>
                    <p className="text-gray-600 mt-2">Upload lessons and generate educational content</p>
                </div>

                <div className="grid md:grid-cols-2 gap-8">
                    {/* Upload Section */}
                    <div className="bg-white rounded-xl shadow-lg p-6">
                        <h2 className="text-2xl font-semibold mb-4">Upload Lesson</h2>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Select PDF or TXT file
                                </label>
                                <input
                                    id="file-input"
                                    type="file"
                                    accept=".pdf,.txt"
                                    onChange={handleFileChange}
                                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
                                />
                            </div>
                            {file && (
                                <div className="p-3 bg-gray-50 rounded-lg">
                                    <p className="text-sm text-gray-600">Selected: {file.name}</p>
                                </div>
                            )}
                            <button
                                onClick={handleUpload}
                                disabled={!file || uploading}
                                className="w-full bg-primary-600 text-white py-2 px-4 rounded-lg hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                            >
                                {uploading ? 'Uploading...' : 'Upload & Generate Content'}
                            </button>
                        </div>
                    </div>

                    {/* Lessons List */}
                    <div className="bg-white rounded-xl shadow-lg p-6">
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-2xl font-semibold">My Lessons</h2>
                            <button
                                onClick={loadLessons}
                                className="text-primary-600 hover:text-primary-700 text-sm"
                            >
                                Refresh
                            </button>
                        </div>
                        <div className="space-y-2 max-h-96 overflow-y-auto">
                            {lessons.length === 0 ? (
                                <p className="text-gray-500 text-center py-8">No lessons yet. Upload your first lesson!</p>
                            ) : (
                                lessons.map((lesson) => (
                                    <div
                                        key={lesson.id}
                                        onClick={() => loadLessonDetails(lesson.id)}
                                        className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                                    >
                                        <h3 className="font-semibold text-gray-800">{lesson.title}</h3>
                                        <p className="text-sm text-gray-500 mt-1">{lesson.filename}</p>
                                        <p className="text-xs text-gray-400 mt-1">
                                            {new Date(lesson.created_at).toLocaleDateString()}
                                        </p>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                </div>

                {/* Lesson Details & Quiz */}
                {selectedLesson && (
                    <div className="mt-8 bg-white rounded-xl shadow-lg p-6">
                        <h2 className="text-2xl font-semibold mb-4">{selectedLesson.title}</h2>

                        {selectedLesson.explanation && (
                            <div className="mb-6">
                                <h3 className="text-xl font-semibold mb-2">Explanation</h3>
                                <p className="text-gray-700 whitespace-pre-wrap">{selectedLesson.explanation}</p>
                            </div>
                        )}

                        {quiz.length > 0 && (
                            <div>
                                <h3 className="text-xl font-semibold mb-4">Quiz (5 MCQs)</h3>
                                <div className="space-y-6">
                                    {quiz.map((item, index) => (
                                        <div key={index} className="border-l-4 border-primary-500 pl-4">
                                            <p className="font-semibold text-gray-800 mb-2">
                                                {index + 1}. {item.question}
                                            </p>
                                            <div className="space-y-2 ml-4">
                                                {item.options.map((option, optIndex) => (
                                                    <div
                                                        key={optIndex}
                                                        className={`p-2 rounded ${optIndex === item.correct_answer
                                                                ? 'bg-green-50 border border-green-200'
                                                                : 'bg-gray-50'
                                                            }`}
                                                    >
                                                        <span className="font-medium mr-2">
                                                            {String.fromCharCode(65 + optIndex)}.
                                                        </span>
                                                        {option}
                                                        {optIndex === item.correct_answer && (
                                                            <span className="ml-2 text-green-600 text-sm">✓ Correct</span>
                                                        )}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    )
}

