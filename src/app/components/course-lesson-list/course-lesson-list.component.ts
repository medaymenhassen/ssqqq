import { Component, OnInit } from '@angular/core';
import { TestService, CourseLesson } from '../../services/test.service';
import { AuthService } from '../../auth.service';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-course-lesson-list',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './course-lesson-list.component.html',
  styleUrls: ['./course-lesson-list.component.scss'],
  providers: [AuthService]
})
export class CourseLessonListComponent implements OnInit {
  lessons: CourseLesson[] = [];
  loading: boolean = false;
  error: string = '';

  userId: number | null = null;

  constructor(
    private testService: TestService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.loadCurrentUser();
    this.loadCourseLessons();
  }

  private loadCurrentUser(): void {
    const currentUser = this.authService.getCurrentUser();
    if (currentUser) {
      this.userId = currentUser.id;
    }
  }

  loadCourseLessons(): void {
    this.loading = true;
    // If user is logged in, we still call getAllCourseLessons which doesn't require access control
    // For individual lesson access, we would pass userId to getCourseLessonById
    this.testService.getAllCourseLessons().subscribe({
      next: (lessons) => {
        this.lessons = lessons;
        this.loading = false;
      },
      error: (error) => {
        this.error = 'Error loading course lessons';
        this.loading = false;
        console.error(error);
      }
    });
  }

  deleteCourseLesson(id: number): void {
    if (confirm('Are you sure you want to delete this course lesson?')) {
      this.testService.deleteCourseLesson(id).subscribe({
        next: () => {
          // Remove the deleted lesson from the list
          this.lessons = this.lessons.filter(lesson => lesson.id !== id);
        },
        error: (error) => {
          this.error = 'Error deleting course lesson';
          console.error(error);
        }
      });
    }
  }

  generateSlug(title: string): string {
    if (!title) return 'lesson';
    return title
      .toLowerCase()
      .trim()
      .replace(/[\s\W-]+/g, '-')
      .replace(/^-+|-+$/g, '');
  }
}