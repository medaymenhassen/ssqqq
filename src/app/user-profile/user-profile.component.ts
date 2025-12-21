import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService, User } from '../auth.service';
import { TestService, CourseLesson } from '../services/test.service';
import { DocumentService, Document } from '../services/document.service';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup } from '@angular/forms';

@Component({
  selector: 'app-user-profile',
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './user-profile.component.html',
  styleUrl: './user-profile.component.scss'
})
export class UserProfileComponent implements OnInit {
  currentUser: User | null = null;
  completedLessons: CourseLesson[] = [];
  serviceLessons: CourseLesson[] = [];
  formationLessons: CourseLesson[] = [];
  userDocuments: Document[] = [];
  documentForm: FormGroup;
  selectedFiles: File[] = [];
  isLoading = false;
  errorMessage = '';
  successMessage = '';

  constructor(
    public route: ActivatedRoute,
    private router: Router,
    private authService: AuthService,
    private testService: TestService,
    private documentService: DocumentService,
    private fb: FormBuilder
  ) {
    this.documentForm = this.fb.group({
      documents: ['']
    });
  }

  ngOnInit(): void {
    // Check if we're viewing a specific user's profile
    const userIdParam = this.route.snapshot.paramMap.get('id');
    
    if (userIdParam) {
      // Viewing another user's profile
      const userId = parseInt(userIdParam, 10);
      // In a real application, you would fetch the user data from the server
      // For now, we'll just load the data for the specified user
      this.loadUserProfileData(userId);
    } else {
      // Viewing current user's profile
      this.authService.currentUser.subscribe(user => {
        this.currentUser = user;
        if (user) {
          this.loadUserProfileData(user.id);
        }
      });
    }
  }

  loadUserProfileData(userId: number): void {
    // If we're viewing another user's profile, we need to fetch their data
    const userIdParam = this.route.snapshot.paramMap.get('id');
    
    if (userIdParam) {
      // We're viewing another user's profile
      this.authService.getUserById(userId).subscribe({
        next: (user) => {
          this.currentUser = user;
          // Load completed lessons
          this.loadCompletedLessons(userId);
          
          // Load user documents
          this.loadUserDocuments(userId);
        },
        error: (error) => {
          console.error('Error loading user data:', error);
        }
      });
    } else {
      // Load completed lessons
      this.loadCompletedLessons(userId);
      
      // Load user documents
      this.loadUserDocuments(userId);
    }
  }

  loadCompletedLessons(userId: number): void {
    // Get completed lessons for the user
    this.testService.getCompletedLessonsForUser(userId).subscribe({
      next: (lessons) => {
        this.completedLessons = lessons;
        this.serviceLessons = lessons.filter(lesson => lesson.isService);
        this.formationLessons = lessons.filter(lesson => !lesson.isService);
      },
      error: (error) => {
        console.error('Error loading completed lessons:', error);
      }
    });
  }

  loadUserDocuments(userId: number): void {
    // Load documents for the current user
    this.documentService.getUserDocuments(userId).subscribe({
      next: (documents) => {
        this.userDocuments = documents;
      },
      error: (error) => {
        console.error('Error loading user documents:', error);
      }
    });
  }

  onFileSelect(event: any): void {
    const files = event.target.files;
    if (files && files.length > 0) {
      this.selectedFiles = Array.from(files);
    }
  }

  onSubmitDocuments(): void {
    if (this.selectedFiles.length > 0 && this.currentUser && this.currentUser.userType) {
      this.isLoading = true;
      this.errorMessage = '';
      this.successMessage = '';

      this.documentService.uploadDocuments(
        this.currentUser.id,
        this.currentUser.userType.id,
        this.selectedFiles
      ).subscribe({
        next: (response) => {
          this.isLoading = false;
          this.successMessage = 'Documents uploaded successfully! They are awaiting admin approval.';
          this.selectedFiles = [];
          // Reload documents
          if (this.currentUser) {
            this.loadUserDocuments(this.currentUser.id);
          }
        },
        error: (error) => {
          this.isLoading = false;
          this.errorMessage = error.error?.message || 'Error uploading documents. Please try again.';
        }
      });
    }
  }

  markLessonAsCompleted(lessonId: number): void {
    if (this.currentUser) {
      this.testService.markLessonAsCompleted(this.currentUser.id, lessonId).subscribe({
        next: () => {
          // Reload completed lessons
          this.loadCompletedLessons(this.currentUser!.id);
          console.log('Lesson marked as completed');
        },
        error: (error) => {
          console.error('Error marking lesson as completed:', error);
        }
      });
    }
  }
}