import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, FormArray, Validators, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { TestService, TestQuestion, TestAnswer } from '../../services/test.service';
import { AuthService, User } from '../../auth.service';
import { CommonModule } from '@angular/common';
import { lastValueFrom } from 'rxjs';

@Component({
  selector: 'app-question-answer-manager',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './question-answer-manager.component.html',
  styleUrls: ['./question-answer-manager.component.scss']
})
export class QuestionAnswerManagerComponent implements OnInit {
  answerForm: FormGroup;
  questionId: number | null = null;
  question: TestQuestion | null = null;
  loading: boolean = false;
  error: string = '';
  success: string = '';
  selectedFiles: Map<number, File[]> = new Map();

  currentUser: User | null = null;

  constructor(
    private fb: FormBuilder,
    private testService: TestService,
    private authService: AuthService,
    private route: ActivatedRoute,
    private router: Router
  ) {
    this.answerForm = this.fb.group({
      answers: this.fb.array([])
    });
  }

  ngOnInit(): void {
    // Get current user
    this.authService.currentUser.subscribe(user => {
      this.currentUser = user;
    });

    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.questionId = +id;
      this.loadQuestion(this.questionId);
    }
  }

  loadQuestion(id: number): void {
    this.loading = true;
    this.testService.getTestQuestionById(id).subscribe({
      next: (question) => {
        this.question = question;
        this.initializeForm(question);
        this.loading = false;
      },
      error: (error) => {
        this.error = 'Error loading question';
        this.loading = false;
        console.error(error);
      }
    });
  }

  initializeForm(question: TestQuestion): void {
    const answersArray = this.answerForm.get('answers') as FormArray;
    
    // Clear existing controls
    while (answersArray.length !== 0) {
      answersArray.removeAt(0);
    }
    
    // Initialize form with existing answers
    if (question.answers && question.answers.length > 0) {
      question.answers.forEach((answer, index) => {
        answersArray.push(this.fb.group({
          id: [answer.id],
          answerText: [answer.answerText, [Validators.required]],
          isLogical: [answer.isLogical || 'pending'],
          isCorrect: [answer.isCorrect || 'pending'],
          answerOrder: [answer.answerOrder]
        }));
      });
    } else {
      // Add at least one empty answer field
      this.addAnswer();
    }
  }
  
  addAnswer(): void {
    const answersArray = this.answerForm.get('answers') as FormArray;
    const answerOrder = answersArray.length + 1;
    
    answersArray.push(this.fb.group({
      id: [null],
      answerText: ['', [Validators.required]],
      isLogical: ['pending'],
      isCorrect: ['pending'],
      answerOrder: [answerOrder]
    }));
  }
  
  removeAnswer(index: number): void {
    const answersArray = this.answerForm.get('answers') as FormArray;
    answersArray.removeAt(index);
    
    // Update answer orders
    this.updateAnswerOrders();
  }
  
  updateAnswerOrders(): void {
    const answersArray = this.answerForm.get('answers') as FormArray;
    answersArray.controls.forEach((control, index) => {
      control.get('answerOrder')?.setValue(index + 1);
    });
  }

  get answers(): FormArray {
    return this.answerForm.get('answers') as FormArray;
  }

  onSubmit(): void {
    if (this.answerForm.valid && this.questionId) {
      this.loading = true;
      this.error = '';
      this.success = '';
      
      const answersData = this.answerForm.value.answers;
      
      // Process each answer
      const observables = answersData.map((answerData: any) => {
        const answer: TestAnswer = {
          id: answerData.id,
          answerText: answerData.answerText,
          isLogical: answerData.isLogical,
          isCorrect: answerData.isCorrect,
          answerOrder: answerData.answerOrder,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          questionId: this.questionId!
        };
        
        // Add userId when creating a new answer
        if (!answerData.id && this.currentUser) {
          answer.userId = this.currentUser.id;
        }
        
        if (answerData.id) {
          // Update existing answer
          return this.testService.updateTestAnswer(answerData.id, answer);
        } else {
          // Create new answer
          return this.testService.createTestAnswer(answer);
        }
      });
      
      // Execute all observables
      Promise.all(observables.map((obs: any) => lastValueFrom(obs))).then(
        (results) => {
          // Upload documents for newly created answers
          const documentUploads = [];
          for (let i = 0; i < results.length; i++) {
            const answer = results[i];
            const files = this.selectedFiles.get(i);
            if (files) {
              // Upload each file for this answer
              for (const file of files) {
                documentUploads.push(
                  lastValueFrom(this.testService.uploadDocumentForTestAnswer(answer.id, file))
                    .then(() => {
                      console.log(`Document uploaded for answer ${answer.id}: ${file.name}`);
                    })
                    .catch((error) => {
                      console.error(`Failed to upload document for answer ${answer.id}:`, error);
                      console.error(`Error details - Status: ${error.status}, Message: ${error.message}, Error:`, error.error);
                      this.error = `Failed to upload document ${file.name} for answer ${answer.id}: ${error.message || error.error || 'Unknown error'}`;
                    })
                );
              }
            }
          }
          
          // Wait for all document uploads to complete
          Promise.all(documentUploads).then(() => {
            this.success = 'Answers and documents saved successfully!';
            this.loading = false;
            this.selectedFiles.clear(); // Clear selected files
            
            // Reload the question to get updated answers
            if (this.questionId) {
              this.loadQuestion(this.questionId);
            }
          }).catch((error) => {
            this.error = 'Answers saved but some documents failed to upload: ' + (error.message || 'Unknown error');
            this.loading = false;
            this.selectedFiles.clear();
            console.error('Document upload error:', error);
            
            // Still reload to show updated answers
            if (this.questionId) {
              this.loadQuestion(this.questionId);
            }
          });
        },
        (error) => {
          this.error = 'Error saving answers';
          this.loading = false;
          console.error(error);
        }
      );
    }
  }

  onCancel(): void {
    this.router.navigate(['/test-questions']);
  }

  onFileSelected(index: number, event: any): void {
    const files: FileList = event.target.files;
    console.log(`File selection event for answer ${index + 1}:`, event);
    if (files && files.length > 0) {
      const fileList: File[] = [];
      for (let i = 0; i < files.length; i++) {
        fileList.push(files[i]);
      }
      this.selectedFiles.set(index, fileList);
      console.log(`Selected ${files.length} files for answer ${index + 1}:`, fileList.map(f => f.name));
    } else {
      this.selectedFiles.delete(index);
      console.log(`No files selected for answer ${index + 1}`);
    }
  }
}