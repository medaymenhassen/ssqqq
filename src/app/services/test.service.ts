import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

// Define interfaces for our DTOs
export interface CourseTest {
  id: number;
  title: string;
  description: string;
  passingScore: number;
  timeLimitMinutes: number;
  createdAt: string;
  updatedAt: string;
  courseId: number;
  questions: TestQuestion[];
}

export interface TestQuestion {
  id: number;
  questionText: string;
  questionOrder: number;
  points: number;
  questionType: string; // MCQ or OPEN_ENDED
  createdAt: string;
  updatedAt: string;
  courseTestId: number;
  userId?: number; // User who created the question
  answers: TestAnswer[];
}

export interface CourseLesson {
  id: number;
  title: string;
  description: string;
  videoUrl: string;
  animation3dUrl: string;
  contentTitle: string;
  contentDescription: string;
  displayOrder: number;
  lessonOrder: number;
  isService: boolean;
  userId?: number; // User who created the lesson
  createdAt: string;
  updatedAt: string;
}

export interface TestAnswer {
  id: number;
  answerText: string;
  isLogical: string;
  isCorrect: string;
  answerOrder: number;
  createdAt: string;
  updatedAt: string;
  questionId: number;
  userId?: number; // User who created the answer
}

@Injectable({
  providedIn: 'root'
})
export class TestService {
  // Service for handling test-related API calls
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  // Get authorization headers
  private getAuthHeaders(): HttpHeaders {
    // Check if we're in browser context
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('accessToken');
      if (token) {
        return new HttpHeaders({
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        });
      }
    }
    // Return default headers if no token or in SSR context
    return new HttpHeaders({
      'Content-Type': 'application/json'
    });
  }

  // CourseTest methods
  getAllCourseTests(): Observable<CourseTest[]> {
    return this.http.get<CourseTest[]>(`${this.apiUrl}/tests/course-tests`, {
      headers: this.getAuthHeaders()
    });
  }

  getCourseTestById(id: number): Observable<CourseTest> {
    return this.http.get<CourseTest>(`${this.apiUrl}/tests/course-tests/${id}`, {
      headers: this.getAuthHeaders()
    });
  }

  createCourseTest(courseTest: CourseTest): Observable<CourseTest> {
    return this.http.post<CourseTest>(`${this.apiUrl}/tests/course-tests`, courseTest, {
      headers: this.getAuthHeaders()
    });
  }

  updateCourseTest(id: number, courseTest: CourseTest): Observable<CourseTest> {
    return this.http.put<CourseTest>(`${this.apiUrl}/tests/course-tests/${id}`, courseTest, {
      headers: this.getAuthHeaders()
    });
  }

  deleteCourseTest(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/tests/course-tests/${id}`, {
      headers: this.getAuthHeaders()
    });
  }

  // TestQuestion methods
  getAllTestQuestions(): Observable<TestQuestion[]> {
    return this.http.get<TestQuestion[]>(`${this.apiUrl}/tests/questions`, {
      headers: this.getAuthHeaders()
    });
  }

  getTestQuestionsByLessonId(lessonId: number): Observable<TestQuestion[]> {
    return this.http.get<TestQuestion[]>(`${this.apiUrl}/tests/questions/lesson/${lessonId}`, {
      headers: this.getAuthHeaders()
    });
  }

  getTestQuestionById(id: number): Observable<TestQuestion> {
    return this.http.get<TestQuestion>(`${this.apiUrl}/tests/questions/${id}`, {
      headers: this.getAuthHeaders()
    });
  }

  createTestQuestion(testQuestion: TestQuestion): Observable<TestQuestion> {
    return this.http.post<TestQuestion>(`${this.apiUrl}/tests/questions`, testQuestion, {
      headers: this.getAuthHeaders()
    });
  }

  updateTestQuestion(id: number, testQuestion: TestQuestion): Observable<TestQuestion> {
    return this.http.put<TestQuestion>(`${this.apiUrl}/tests/questions/${id}`, testQuestion, {
      headers: this.getAuthHeaders()
    });
  }

  deleteTestQuestion(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/tests/questions/${id}`, {
      headers: this.getAuthHeaders()
    });
  }

  // TestAnswer methods
  getAllTestAnswers(): Observable<TestAnswer[]> {
    return this.http.get<TestAnswer[]>(`${this.apiUrl}/tests/answers`, {
      headers: this.getAuthHeaders()
    });
  }

  getTestAnswerById(id: number): Observable<TestAnswer> {
    return this.http.get<TestAnswer>(`${this.apiUrl}/tests/answers/${id}`, {
      headers: this.getAuthHeaders()
    });
  }

  createTestAnswer(testAnswer: TestAnswer): Observable<TestAnswer> {
    return this.http.post<TestAnswer>(`${this.apiUrl}/tests/answers`, testAnswer, {
      headers: this.getAuthHeaders()
    });
  }

  updateTestAnswer(id: number, testAnswer: TestAnswer): Observable<TestAnswer> {
    return this.http.put<TestAnswer>(`${this.apiUrl}/tests/answers/${id}`, testAnswer, {
      headers: this.getAuthHeaders()
    });
  }

  deleteTestAnswer(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/tests/answers/${id}`, {
      headers: this.getAuthHeaders()
    });
  }
  
  // CourseLesson methods
  getAllCourseLessons(): Observable<CourseLesson[]> {
    return this.http.get<CourseLesson[]>(`${this.apiUrl}/course-lessons`, {
      headers: this.getAuthHeaders()
    });
  }
  
  getCourseLessonById(id: number, userId?: number): Observable<CourseLesson> {
    let url = `${this.apiUrl}/course-lessons/${id}`;
    if (userId) {
      url += `?userId=${userId}`;
    }
    return this.http.get<CourseLesson>(url, {
      headers: this.getAuthHeaders()
    });
  }
  
  createCourseLesson(courseLesson: CourseLesson): Observable<CourseLesson> {
    return this.http.post<CourseLesson>(`${this.apiUrl}/course-lessons`, courseLesson, {
      headers: this.getAuthHeaders()
    });
  }
  
  updateCourseLesson(id: number, courseLesson: CourseLesson): Observable<CourseLesson> {
    return this.http.put<CourseLesson>(`${this.apiUrl}/course-lessons/${id}`, courseLesson, {
      headers: this.getAuthHeaders()
    });
  }
  
  deleteCourseLesson(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/course-lessons/${id}`, {
      headers: this.getAuthHeaders()
    });
  }

  // Get all lessons for a user
  getLessonsForUser(userId: number): Observable<CourseLesson[]> {
    return this.http.get<CourseLesson[]>(`${this.apiUrl}/course-lessons/user/${userId}`);
  }
  
  // Get completed lessons for a user
  getCompletedLessonsForUser(userId: number): Observable<CourseLesson[]> {
    return this.http.get<CourseLesson[]>(`${this.apiUrl}/course-lessons/user/${userId}/completed`);
  }

  // Mark a lesson as completed for a user
  markLessonAsCompleted(userId: number, lessonId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/course-lessons/user/${userId}/lesson/${lessonId}/complete`, {}, {
      headers: this.getAuthHeaders()
    });
  }

  /**
   * Upload a document for a test answer
   * @param testAnswerId The ID of the test answer
   * @param file The file to upload
   * @returns Observable with the uploaded document
   */
  uploadDocumentForTestAnswer(testAnswerId: number, file: File): Observable<any> {
    const formData = new FormData();
    formData.append('testAnswerId', testAnswerId.toString());
    formData.append('file', file);
    
    // Create headers without Content-Type for multipart/form-data
    const headers = this.getAuthHeaders().delete('Content-Type');
    
    return this.http.post(`${this.apiUrl}/documents/upload-for-test-answer`, formData, {
      headers: headers
    });
  }
}