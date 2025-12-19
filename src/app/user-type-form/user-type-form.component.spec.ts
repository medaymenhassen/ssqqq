import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UserTypeFormComponent } from './user-type-form.component';

describe('UserTypeFormComponent', () => {
  let component: UserTypeFormComponent;
  let fixture: ComponentFixture<UserTypeFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UserTypeFormComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UserTypeFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
