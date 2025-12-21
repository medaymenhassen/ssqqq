import { Component, OnInit } from '@angular/core';
import { TestService, CourseLesson } from '../../services/test.service';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-course-lesson-list',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './course-lesson-list.component.html',
  styleUrls: ['./course-lesson-list.component.scss']
})
export class CourseLessonListComponent implements OnInit {
  lessons: CourseLesson[] = [];
  loading: boolean = false;
  error: string = '';

  constructor(private testService: TestService) {}

  ngOnInit(): void {
    this.loadCourseLessons();
  }

  loadCourseLessons(): void {
    this.loading = true;
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
}