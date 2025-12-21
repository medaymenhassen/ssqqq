import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { TestService, CourseLesson } from '../../services/test.service';
import { AuthService, User } from '../../auth.service';
import { DocumentService } from '../../services/document.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-course-lesson-form',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './course-lesson-form.component.html',
  styleUrls: ['./course-lesson-form.component.scss']
})
export class CourseLessonFormComponent implements OnInit {
  lessonForm: FormGroup;
  isEditMode: boolean = false;
  lessonID: number | null = null;
  loading: boolean = false;
  error: string = '';

  currentUser: User | null = null;

  selectedVideoFile: File | null = null;
  selected3DModelFile: File | null = null;
  
  constructor(
    private fb: FormBuilder,
    private testService: TestService,
    private authService: AuthService,
    private documentService: DocumentService,
    private route: ActivatedRoute,
    private router: Router
  ) {
    this.lessonForm = this.fb.group({
      title: ['', [Validators.required, Validators.minLength(2)]],
      description: ['', [Validators.maxLength(1000)]],
      videoUrl: [''],
      animation3dUrl: [''],
      contentTitle: [''],
      contentDescription: ['', [Validators.maxLength(2000)]],
      displayOrder: [0],
      lessonOrder: [0],
      isService: [false]
    });
  }

  ngOnInit(): void {
    // Get current user
    this.authService.currentUser.subscribe(user => {
      this.currentUser = user;
    });

    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.isEditMode = true;
      this.lessonID = +id;
      this.loadCourseLesson(this.lessonID);
    }
  }
  
  onVideoFileSelected(event: any): void {
    const file: File = event.target.files[0];
    if (file) {
      this.selectedVideoFile = file;
    }
  }
  
  on3DModelFileSelected(event: any): void {
    const file: File = event.target.files[0];
    if (file) {
      this.selected3DModelFile = file;
    }
  }

  loadCourseLesson(id: number): void {
    this.loading = true;
    this.testService.getCourseLessonById(id).subscribe({
      next: (lesson) => {
        this.lessonForm.patchValue({
          title: lesson.title,
          description: lesson.description,
          videoUrl: lesson.videoUrl,
          animation3dUrl: lesson.animation3dUrl,
          contentTitle: lesson.contentTitle,
          contentDescription: lesson.contentDescription,
          displayOrder: lesson.displayOrder,
          lessonOrder: lesson.lessonOrder,
          isService: lesson.isService
        });
        this.loading = false;
      },
      error: (error) => {
        this.error = 'Error loading course lesson';
        this.loading = false;
        console.error(error);
      }
    });
  }

  onSubmit(): void {
    if (this.lessonForm.valid) {
      this.loading = true;
      this.error = '';

      const lesson: CourseLesson = this.lessonForm.value;
      // Add userId when creating a new lesson
      if (!this.isEditMode && this.currentUser) {
        lesson.userId = this.currentUser.id;
      }

      if (this.isEditMode && this.lessonID) {
        // Update existing lesson
        this.testService.updateCourseLesson(this.lessonID, lesson).subscribe({
          next: (updatedLesson) => {
            // Upload files if selected
            this.uploadFiles(updatedLesson.id);
            this.loading = false;
            this.router.navigate(['/course-lessons']);
          },
          error: (error) => {
            this.loading = false;
            this.error = 'Error updating course lesson';
            console.error(error);
          }
        });
      } else {
        // Create new lesson
        this.testService.createCourseLesson(lesson).subscribe({
          next: (newLesson) => {
            // Upload files if selected
            this.uploadFiles(newLesson.id);
            this.loading = false;
            this.router.navigate(['/course-lessons']);
          },
          error: (error) => {
            this.loading = false;
            this.error = 'Error creating course lesson';
            console.error(error);
          }
        });
      }
    }
  }
  
  private uploadFiles(lessonId: number): void {
    // Upload video file if selected
    if (this.selectedVideoFile && this.currentUser) {
      this.documentService.uploadDocumentForLessonOrAnalysis(this.currentUser.id, `lesson_${lessonId}_video`, this.selectedVideoFile).subscribe({
        next: (document) => {
          console.log('📹 Video file uploaded for lesson:', document);
        },
        error: (error) => {
          console.error('❌ Error uploading video file:', error);
        }
      });
    }
    
    // Upload 3D model file if selected
    if (this.selected3DModelFile && this.currentUser) {
      this.documentService.uploadDocumentForLessonOrAnalysis(this.currentUser.id, `lesson_${lessonId}_3d_model`, this.selected3DModelFile).subscribe({
        next: (document) => {
          console.log('🎮 3D model file uploaded for lesson:', document);
        },
        error: (error) => {
          console.error('❌ Error uploading 3D model file:', error);
        }
      });
    }
  }

  onCancel(): void {
    this.router.navigate(['/course-lessons']);
  }
}