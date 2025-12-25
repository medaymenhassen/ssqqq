import { Routes } from '@angular/router';
import { VideoComponent } from './video/video.component';
import { LoginComponent } from './login/login.component';
import { RegisterComponent } from './register/register.component';
import { UserTypeListComponent } from './user-type-list/user-type-list.component';
import { UserTypeFormComponent } from './user-type-form/user-type-form.component';
import { UserListComponent } from './user-list/user-list.component';
import { DataViewerComponent } from './data-viewer/data-viewer.component';
import { CourseTestFormComponent } from './components/course-test-form/course-test-form.component';
import { CourseTestListComponent } from './components/course-test-list/course-test-list.component';
import { TestQuestionFormComponent } from './components/test-question-form/test-question-form.component';
import { TestQuestionListComponent } from './components/test-question-list/test-question-list.component';
import { TestAnswerFormComponent } from './components/test-answer-form/test-answer-form.component';
import { QuestionAnswerManagerComponent } from './components/question-answer-manager/question-answer-manager.component';
import { CourseLessonListComponent } from './components/course-lesson-list/course-lesson-list.component';
import { CourseLessonFormComponent } from './components/course-lesson-form/course-lesson-form.component';
import { CourseLessonDetailComponent } from './components/course-lesson-detail/course-lesson-detail.component';
import { UserProfileComponent } from './user-profile/user-profile.component';
import { ImageAnalysisComponent } from './image-analysis/image-analysis.component';
import { OfferListComponent } from './offer/offer-list.component';
import { OfferCreateComponent } from './offer/offer-create.component';
import { OfferEditComponent } from './offer/offer-edit.component';
import { LandingComponent } from './landing/landing.component';

export const routes: Routes = [
  { path: '', component: LandingComponent, pathMatch: 'full' },
  { path: 'bodyanalytics', component: VideoComponent },
  { path: 'image-analysis', component: ImageAnalysisComponent },
  { path: 'data', component: DataViewerComponent },
  { path: 'login', component: LoginComponent},
  { path: 'register', component: RegisterComponent},
  { path: 'user-types', component: UserTypeListComponent},
  { path: 'user-types/create', component: UserTypeFormComponent},
  { path: 'user-types/:id/edit', component: UserTypeFormComponent },
  { path: 'users', component: UserListComponent },
  { path: 'course-tests', component: CourseTestListComponent },
  { path: 'course-tests/create', component: CourseTestFormComponent },
  { path: 'course-tests/:id/edit', component: CourseTestFormComponent },
  { path: 'test-questions', component: TestQuestionListComponent },
  { path: 'test-questions/create', component: TestQuestionFormComponent },
  { path: 'test-questions/create/:courseTestId', component: TestQuestionFormComponent },
  { path: 'test-questions/:id/edit', component: TestQuestionFormComponent },
  { path: 'test-questions/:id/answers', component: QuestionAnswerManagerComponent },
  { path: 'test-answers/create', component: TestAnswerFormComponent },
  { path: 'test-answers/:id/edit', component: TestAnswerFormComponent },
  { path: 'course-lessons', component: CourseLessonListComponent },
  { path: 'course-lessons/create', component: CourseLessonFormComponent },
  { path: 'course-lessons/:id/edit', component: CourseLessonFormComponent },
  { path: 'course-lessons/:idSlug', component: CourseLessonDetailComponent },
  { path: 'profile', component: UserProfileComponent },
  { path: 'profile/:id', component: UserProfileComponent },
  { path: 'offers', component: OfferListComponent },
  { path: 'offers/create', component: OfferCreateComponent },
  { path: 'offers/edit/:id', component: OfferEditComponent },
  { path: '**', redirectTo: '/' }
];
