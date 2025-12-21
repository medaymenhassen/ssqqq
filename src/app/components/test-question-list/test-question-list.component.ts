import { Component, OnInit } from '@angular/core';
import { TestService, TestQuestion, TestAnswer } from '../../services/test.service';
import { CommonModule } from '@angular/common';
import { RouterModule, ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-test-question-list',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './test-question-list.component.html',
  styleUrls: ['./test-question-list.component.scss']
})
export class TestQuestionListComponent implements OnInit {
  questions: TestQuestion[] = [];
  loading: boolean = false;
  error: string = '';

  constructor(private testService: TestService, private route: ActivatedRoute) {}

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      if (params['lessonId']) {
        // Filter questions by lessonId
        this.loadTestQuestionsByLessonId(params['lessonId']);
      } else {
        this.loadTestQuestions();
      }
    });
  }

  loadTestQuestions(): void {
    this.loading = true;
    this.testService.getAllTestQuestions().subscribe({
      next: (questions) => {
        this.questions = questions;
        this.loading = false;
      },
      error: (error) => {
        this.error = 'Error loading test questions';
        this.loading = false;
        console.error(error);
      }
    });
  }

  loadTestQuestionsByLessonId(lessonId: string): void {
    this.loading = true;
    this.testService.getTestQuestionsByLessonId(parseInt(lessonId)).subscribe({
      next: (questions) => {
        this.questions = questions;
        this.loading = false;
      },
      error: (error) => {
        this.error = 'Error loading test questions';
        this.loading = false;
        console.error(error);
      }
    });
  }

  deleteTestQuestion(id: number): void {
    if (confirm('Are you sure you want to delete this test question?')) {
      this.testService.deleteTestQuestion(id).subscribe({
        next: () => {
          // Remove the deleted question from the list
          this.questions = this.questions.filter(question => question.id !== id);
        },
        error: (error) => {
          this.error = 'Error deleting test question';
          console.error(error);
        }
      });
    }
  }

  getAnswersForQuestion(questionId: number): TestAnswer[] {
    // Find the question and return its answers
    const question = this.questions.find(q => q.id === questionId);
    return question ? question.answers : [];
  }
}