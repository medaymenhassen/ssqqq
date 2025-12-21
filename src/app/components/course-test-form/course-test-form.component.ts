import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { TestService, CourseTest, CourseLesson } from '../../services/test.service';
import { AuthService, User } from '../../auth.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-course-test-form',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './course-test-form.component.html',
  styleUrls: ['./course-test-form.component.scss']
})
export class CourseTestFormComponent implements OnInit {
  courseTestForm: FormGroup;
  isEditMode: boolean = false;
  courseTestID: number | null = null;
  loading: boolean = false;
  error: string = '';
  courseLessons: CourseLesson[] = [];

  currentUser: User | null = null;
  
  constructor(
    private fb: FormBuilder,
    private testService: TestService,
    private authService: AuthService,
    private route: ActivatedRoute,
    private router: Router
  ) {
    this.courseTestForm = this.fb.group({
      title: ['', [Validators.required, Validators.minLength(2)]],
      description: ['', [Validators.maxLength(1000)]],
      passingScore: [70, [Validators.min(0), Validators.max(100)]],
      timeLimitMinutes: ['', [Validators.min(1)]],
      courseId: [''],
      lessonId: ['']
    });
  }

  ngOnInit(): void {
    // Get current user
    this.authService.currentUser.subscribe(user => {
      this.currentUser = user;
      // Load course lessons for dropdown filtered by current user
      if (this.currentUser) {
        this.loadCourseLessonsForUser(this.currentUser.id);
      }
    });
    
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.isEditMode = true;
      this.courseTestID = +id;
      this.loadCourseTest(this.courseTestID);
    }
  }

  loadCourseTest(id: number): void {
    this.loading = true;
    this.testService.getCourseTestById(id).subscribe({
      next: (courseTest) => {
        this.courseTestForm.patchValue({
          title: courseTest.title,
          description: courseTest.description,
          passingScore: courseTest.passingScore,
          timeLimitMinutes: courseTest.timeLimitMinutes,
          courseId: courseTest.courseId
        });
        this.loading = false;
      },
      error: (error) => {
        this.error = 'Error loading course test';
        this.loading = false;
        console.error(error);
      }
    });
  }
  
  loadCourseLessonsForUser(userId: number): void {
    this.testService.getLessonsForUser(userId).subscribe({
      next: (courseLessons) => {
        this.courseLessons = courseLessons;
      },
      error: (error) => {
        console.error('Error loading course lessons for user:', error);
      }
    });
  }

  onSubmit(): void {
    if (this.courseTestForm.valid) {
      this.loading = true;
      this.error = '';

      const courseTest: CourseTest = this.courseTestForm.value;

      if (this.isEditMode && this.courseTestID) {
        // Update existing course test
        this.testService.updateCourseTest(this.courseTestID, courseTest).subscribe({
          next: (updatedCourseTest) => {
            this.loading = false;
            this.router.navigate(['/course-tests']);
          },
          error: (error) => {
            this.loading = false;
            if (error.message) {
              this.error = error.message;
            } else {
              this.error = 'Error updating course test. You must be an administrator to perform this action.';
            }
            console.error(error);
          }
        });
      } else {
        // Create new course test
        this.testService.createCourseTest(courseTest).subscribe({
          next: (newCourseTest) => {
            this.loading = false;
            this.router.navigate(['/course-tests']);
          },
          error: (error) => {
            this.loading = false;
            if (error.message) {
              this.error = error.message;
            } else {
              this.error = 'Error creating course test. You must be an administrator to perform this action.';
            }
            console.error(error);
          }
        });
      }
    }
  }

  onCancel(): void {
    this.router.navigate(['/course-tests']);
  }
}