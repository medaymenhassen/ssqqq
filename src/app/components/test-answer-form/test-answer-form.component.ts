import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { TestService, TestAnswer } from '../../services/test.service';
import { AuthService, User } from '../../auth.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-test-answer-form',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './test-answer-form.component.html',
  styleUrls: ['./test-answer-form.component.scss']
})
export class TestAnswerFormComponent implements OnInit {
  answerForm: FormGroup;
  isEditMode: boolean = false;
  answerID: number | null = null;
  loading: boolean = false;
  error: string = '';
  selectedFile: File | null = null;

  currentUser: User | null = null;

  constructor(
    private fb: FormBuilder,
    private testService: TestService,
    private authService: AuthService,
    private route: ActivatedRoute,
    private router: Router
  ) {
    this.answerForm = this.fb.group({
      answerText: ['', [Validators.required, Validators.minLength(1)]],
      isLogical: ['false'],
      isCorrect: ['false'],
      answerOrder: ['', [Validators.required, Validators.min(1)]],
      questionId: ['', [Validators.required]],
      document: [null]
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
      this.answerID = +id;
      this.loadAnswer(this.answerID);
    }
  }
  
  onFileSelected(event: any): void {
    const file: File = event.target.files[0];
    if (file) {
      this.selectedFile = file;
    }
  }

  loadAnswer(id: number): void {
    this.loading = true;
    this.testService.getTestAnswerById(id).subscribe({
      next: (answer) => {
        this.answerForm.patchValue({
          answerText: answer.answerText,
          isLogical: answer.isLogical.toString(),
          isCorrect: answer.isCorrect.toString(),
          answerOrder: answer.answerOrder,
          questionId: answer.questionId
        });
        this.loading = false;
      },
      error: (error) => {
        this.error = 'Error loading answer';
        this.loading = false;
        console.error(error);
      }
    });
  }

  onSubmit(): void {
    if (this.answerForm.valid) {
      this.loading = true;
      this.error = '';

      // Convert string values to booleans
      const formValue = this.answerForm.value;
      const answer: TestAnswer = {
        ...formValue,
        isLogical: formValue.isLogical === 'true',
        isCorrect: formValue.isCorrect === 'true'
      };
      // Add userId when creating a new answer
      if (!this.isEditMode && this.currentUser) {
        answer.userId = this.currentUser.id;
      };

      if (this.isEditMode && this.answerID) {
        // Update existing answer
        this.testService.updateTestAnswer(this.answerID, answer).subscribe({
          next: (updatedAnswer) => {
            // Upload document if selected
            if (this.selectedFile) {
              this.testService.uploadDocumentForTestAnswer(updatedAnswer.id, this.selectedFile).subscribe({
                next: (document) => {
                  console.log('Document uploaded successfully:', document);
                  this.loading = false;
                  this.router.navigate(['/test-answers']);
                },
                error: (error) => {
                  this.loading = false;
                  this.error = 'Answer updated but failed to upload document: ' + error.message;
                  console.error(error);
                }
              });
            } else {
              this.loading = false;
              this.router.navigate(['/test-answers']);
            }
          },
          error: (error) => {
            this.loading = false;
            if (error.message) {
              this.error = error.message;
            } else {
              this.error = 'Error updating answer. You must be an administrator to perform this action.';
            }
            console.error(error);
          }
        });
      } else {
        // Create new answer
        this.testService.createTestAnswer(answer).subscribe({
          next: (newAnswer) => {
            // Upload document if selected
            if (this.selectedFile) {
              this.testService.uploadDocumentForTestAnswer(newAnswer.id, this.selectedFile).subscribe({
                next: (document) => {
                  console.log('Document uploaded successfully:', document);
                  this.loading = false;
                  this.router.navigate(['/test-answers']);
                },
                error: (error) => {
                  this.loading = false;
                  this.error = 'Answer created but failed to upload document: ' + error.message;
                  console.error(error);
                }
              });
            } else {
              this.loading = false;
              this.router.navigate(['/test-answers']);
            }
          },
          error: (error) => {
            this.loading = false;
            if (error.message) {
              this.error = error.message;
            } else {
              this.error = 'Error creating answer. You must be an administrator to perform this action.';
            }
            console.error(error);
          }
        });
      }
    }
  }

  onCancel(): void {
    this.router.navigate(['/test-answers']);
  }
}