import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { TestService, TestQuestion, CourseTest, CourseLesson } from '../../services/test.service';
import { AuthService, User } from '../../auth.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-test-question-form',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './test-question-form.component.html',
  styleUrls: ['./test-question-form.component.scss']
})
export class TestQuestionFormComponent implements OnInit {
  questionForm: FormGroup;
  isEditMode: boolean = false;
  questionID: number | null = null;
  courseTestID: number | null = null;
  loading: boolean = false;
  error: string = '';
  courseTests: CourseTest[] = [];
  courseLessons: CourseLesson[] = [];

  questionTypes = [
    { value: 'MCQ', label: 'Multiple Choice Question' },
    { value: 'OPEN_ENDED', label: 'Open Ended Question' }
  ];

  currentUser: User | null = null;

  constructor(
    private fb: FormBuilder,
    private testService: TestService,
    private authService: AuthService,
    private route: ActivatedRoute,
    private router: Router
  ) {
    this.questionForm = this.fb.group({
      questionText: ['', [Validators.required, Validators.minLength(2)]],
      questionOrder: ['', [Validators.required, Validators.min(1)]],
      points: [1, [Validators.min(1)]],
      questionType: ['OPEN_ENDED', [Validators.required]]
    });
  }

  ngOnInit(): void {
    // Get current user
    this.authService.currentUser.subscribe(user => {
      this.currentUser = user;
    });

    // Load course tests and lessons
    this.loadCourseTests();
    this.loadCourseLessons();
    
    const id = this.route.snapshot.paramMap.get('id');
    const courseTestId = this.route.snapshot.paramMap.get('courseTestId');
    
    if (id) {
      this.isEditMode = true;
      this.questionID = +id;
      this.loadQuestion(this.questionID);
    } else if (courseTestId) {
      // Creating a new question for a specific course test
      this.courseTestID = +courseTestId;
      this.questionForm.patchValue({
        courseTestId: this.courseTestID
      });
    }
  }
  
  loadCourseTests(): void {
    this.testService.getAllCourseTests().subscribe({
      next: (courseTests) => {
        this.courseTests = courseTests;
      },
      error: (error) => {
        console.error('Error loading course tests:', error);
      }
    });
  }
  
  loadCourseLessons(): void {
    this.testService.getAllCourseLessons().subscribe({
      next: (courseLessons) => {
        this.courseLessons = courseLessons;
      },
      error: (error) => {
        console.error('Error loading course lessons:', error);
      }
    });
  }

  loadQuestion(id: number): void {
    this.loading = true;
    this.testService.getTestQuestionById(id).subscribe({
      next: (question) => {
        this.questionForm.patchValue({
          questionText: question.questionText,
          questionOrder: question.questionOrder,
          points: question.points,
          questionType: question.questionType,
          courseTestId: question.courseTestId
        });
        this.loading = false;
      },
      error: (error) => {
        this.error = 'Error loading question';
        this.loading = false;
        console.error(error);
      }
    });
  }

  onSubmit(): void {
    if (this.questionForm.valid) {
      this.loading = true;
      this.error = '';

      const question: TestQuestion = this.questionForm.value;
      // Add courseTestId when creating a new question
      if (!this.isEditMode && this.courseTestID) {
        question.courseTestId = this.courseTestID;
      }
      // Add userId when creating a new question
      if (!this.isEditMode && this.currentUser) {
        question.userId = this.currentUser.id;
      }

      if (this.isEditMode && this.questionID) {
        // Update existing question
        this.testService.updateTestQuestion(this.questionID, question).subscribe({
          next: (updatedQuestion) => {
            this.loading = false;
            this.router.navigate(['/test-questions']);
          },
          error: (error) => {
            this.loading = false;
            if (error.message) {
              this.error = error.message;
            } else {
              this.error = 'Error updating question. You must be an administrator to perform this action.';
            }
            console.error(error);
          }
        });
      } else {
        // Create new question
        this.testService.createTestQuestion(question).subscribe({
          next: (newQuestion) => {
            this.loading = false;
            this.router.navigate(['/test-questions']);
          },
          error: (error) => {
            this.loading = false;
            if (error.message) {
              this.error = error.message;
            } else {
              this.error = 'Error creating question. You must be an administrator to perform this action.';
            }
            console.error(error);
          }
        });
      }
    }
  }

  onCancel(): void {
    this.router.navigate(['/test-questions']);
  }
}