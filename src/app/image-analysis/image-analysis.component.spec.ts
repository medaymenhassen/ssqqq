import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ImageAnalysisComponent } from './image-analysis.component';

describe('ImageAnalysisComponent', () => {
  let component: ImageAnalysisComponent;
  let fixture: ComponentFixture<ImageAnalysisComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ImageAnalysisComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(ImageAnalysisComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});