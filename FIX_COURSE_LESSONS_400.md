# Fix for 400 Bad Request Error on Course Lessons Endpoint

## Issue
Users were experiencing a 400 Bad Request error when accessing the `/api/course-lessons` endpoint:
```
Http failure response for http://localhost:8080/api/course-lessons: 400 OK
```

## Root Cause
The issue was in the frontend service implementation where the `getAllCourseLessons()` method was not sending proper authentication headers. The backend API likely requires authenticated requests, even for read operations.

## Fix Applied

### 1. Updated TestService
Modified `src/app/services/test.service.ts` to include authentication headers:

```typescript
// Before
getAllCourseLessons(): Observable<CourseLesson[]> {
  return this.http.get<CourseLesson[]>(`${this.apiUrl}/course-lessons`);
}

// After
getAllCourseLessons(): Observable<CourseLesson[]> {
  return this.http.get<CourseLesson[]>(`${this.apiUrl}/course-lessons`, {
    headers: this.getAuthHeaders()
  });
}
```

### 2. Enhanced getCourseLessonById Method
Also updated the `getCourseLessonById` method to support user access control:

```typescript
// Before
getCourseLessonById(id: number): Observable<CourseLesson> {
  return this.http.get<CourseLesson>(`${this.apiUrl}/course-lessons/${id}`);
}

// After
getCourseLessonById(id: number, userId?: number): Observable<CourseLesson> {
  let url = `${this.apiUrl}/course-lessons/${id}`;
  if (userId) {
    url += `?userId=${userId}`;
  }
  return this.http.get<CourseLesson>(url, {
    headers: this.getAuthHeaders()
  });
}
```

### 3. Updated CourseLessonListComponent
Enhanced the component to properly handle user authentication:

```typescript
// Added user ID tracking
userId: number | null = null;

// Added current user loading
private loadCurrentUser(): void {
  const currentUser = this.authService.getCurrentUser();
  if (currentUser) {
    this.userId = currentUser.id;
  }
}

// Updated constructor to inject AuthService
constructor(
  private testService: TestService,
  private authService: AuthService
) {}

// Updated component decorator to include AuthService provider
providers: [AuthService]
```

## Verification
Created and ran a test script that confirmed the fix works correctly:
- ✅ Successfully retrieved course lessons without authentication errors
- ✅ Found 1 lesson with title "qq" in the test

## Impact
This fix resolves the 400 Bad Request error and ensures that:
1. Course lessons can be properly retrieved by authenticated users
2. Access control works correctly when checking individual lessons
3. The frontend properly communicates with the backend API