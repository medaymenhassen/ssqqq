import { Component, OnInit } from '@angular/core';
import { TestService, CourseTest } from '../../services/test.service';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-course-test-list',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './course-test-list.component.html',
  styleUrls: ['./course-test-list.component.scss']
})
export class CourseTestListComponent implements OnInit {
  courseTests: CourseTest[] = [];
  loading: boolean = false;
  error: string = '';

  constructor(private testService: TestService) {}

  ngOnInit(): void {
    this.loadCourseTests();
  }

  loadCourseTests(): void {
    this.loading = true;
    this.testService.getAllCourseTests().subscribe({
      next: (tests) => {
        this.courseTests = tests;
        this.loading = false;
      },
      error: (error) => {
        this.error = 'Error loading course tests';
        this.loading = false;
        console.error(error);
      }
    });
  }

  deleteCourseTest(id: number): void {
    if (confirm('Are you sure you want to delete this course test?')) {
      this.testService.deleteCourseTest(id).subscribe({
        next: () => {
          // Remove the deleted test from the list
          this.courseTests = this.courseTests.filter(test => test.id !== id);
        },
        error: (error) => {
          this.error = 'Error deleting course test';
          console.error(error);
        }
      });
    }
  }
}