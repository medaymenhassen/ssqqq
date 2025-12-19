import { Routes } from '@angular/router';
import { VideoComponent } from './video/video.component';
import { LoginComponent } from './login/login.component';
import { RegisterComponent } from './register/register.component';
import { UserTypeListComponent } from './user-type-list/user-type-list.component';
import { UserTypeFormComponent } from './user-type-form/user-type-form.component';
import { UserListComponent } from './user-list/user-list.component';
import { DataViewerComponent } from './data-viewer/data-viewer.component';

export const routes: Routes = [
  { path: '', redirectTo: '/bodyanalytics', pathMatch: 'full' },
  { path: 'bodyanalytics', component: VideoComponent },
  { path: 'data', component: DataViewerComponent },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'user-types', component: UserTypeListComponent },
  { path: 'user-types/create', component: UserTypeFormComponent },
  { path: 'user-types/:id/edit', component: UserTypeFormComponent },
  { path: 'users', component: UserListComponent },
  { path: '**', redirectTo: '/bodyanalytics' }
];
