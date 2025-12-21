import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { TestService, CourseLesson } from '../../services/test.service';
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

  constructor(
    private fb: FormBuilder,
    private testService: TestService,
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
      lessonOrder: [0]
    });
  }

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.isEditMode = true;
      this.lessonID = +id;
      this.loadCourseLesson(this.lessonID);
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
          lessonOrder: lesson.lessonOrder
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

      if (this.isEditMode && this.lessonID) {
        // Update existing lesson
        this.testService.updateCourseLesson(this.lessonID, lesson).subscribe({
          next: (updatedLesson) => {
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

  onCancel(): void {
    this.router.navigate(['/course-lessons']);
  }
}