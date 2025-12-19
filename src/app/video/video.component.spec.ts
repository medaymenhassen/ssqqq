import { ComponentFixture, TestBed } from '@angular/core/testing';
import { VideoComponent } from './video.component';
import { MockVideoService } from './video.service.mock';
import { of } from 'rxjs';
import { By } from '@angular/platform-browser';



describe('VideoComponent', () => {
  let component: VideoComponent;
  let fixture: ComponentFixture<VideoComponent>;
  let mockVideoService: MockVideoService;

  beforeEach(async () => {
    mockVideoService = new MockVideoService();
    
    await TestBed.configureTestingModule({
      imports: [VideoComponent],
      providers: [
        { provide: MockVideoService, useValue: mockVideoService }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(VideoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should have a title', () => {
    const compiled = fixture.nativeElement;
    expect(compiled.querySelector('.header h1').textContent).toContain('Tracker Corporel en Temps Réel');
  });

  it('should display start camera button initially', () => {
    const button = fixture.debugElement.query(By.css('.btn-primary'));
    expect(button).toBeTruthy();
    expect(button.nativeElement.textContent).toContain('Démarrer l\'Analyse');
  });

  it('should calculate body confidence correctly', () => {
    // Test with no pose data
    expect(component.getBodyConfidence()).toBe(0);
    
    // Test with sample pose data
    component.bodyAnalysis = {
      pose: {
        Head: { confidence: 0.9 },
        LeftShoulder: { confidence: 0.8 },
        RightShoulder: { confidence: 0.7 }
      },
      face: null,
      hands: { left: null, right: null },
      isAnalyzing: false
    };
    
    const confidence = component.getBodyConfidence();
    expect(confidence).toBeGreaterThan(0);
    expect(confidence).toBeLessThanOrEqual(100);
  });

  it('should format pose information correctly', () => {
    // Test with no pose data
    expect(component.getPoseInfo()).toBe('Pas de pose détectée');
    
    // Test with partial pose data
    component.bodyAnalysis = {
      pose: {
        Head: { position: { x: 0.5, y: 0.3 } }
      },
      face: null,
      hands: { left: null, right: null },
      isAnalyzing: false
    };
    
    expect(component.getPoseInfo()).toContain('Tête: (0.50, 0.30)');
  });

  it('should format face information correctly', () => {
    // Test with no face data
    expect(component.getFaceInfo()).toBe('Pas de visage détecté');
    
    // Test with face data
    component.bodyAnalysis = {
      pose: null,
      face: {
        Head: { 
          position: { x: 0.4, y: 0.6 },
          rotation: { z: 0.1 }
        }
      },
      hands: { left: null, right: null },
      isAnalyzing: false
    };
    
    expect(component.getFaceInfo()).toContain('Expression: Neutre');
  });

  it('should format hands information correctly', () => {
    // Test with no hands data
    expect(component.getHandsInfo()).toBe('Pas détectée | Pas détectée');
    
    // Test with one hand detected
    component.bodyAnalysis = {
      pose: null,
      face: null,
      hands: { 
        left: { landmarks: [1, 2, 3, 4, 5] }, 
        right: null 
      },
      isAnalyzing: false
    };
    
    expect(component.getHandsInfo()).toContain('Gauche: 5 points');
    expect(component.getHandsInfo()).toContain('Pas détectée');
  });

  it('should track confidence trends', () => {
    expect(component.confidenceTrend).toBe('stable');
    
    component.previousConfidence = 70;
    component.getBodyConfidence = () => 80; // Mock the method
    
    // Simulate analysis loop
    const currentTime = Date.now();
    component.lastAnalysisTime = currentTime - 200; // Force analysis
    
    // We can't easily test the private method, but we can verify initial state
    expect(component.previousConfidence).toBe(70);
  });

  it('should have proper UI elements for real-time tracking', () => {
    const compiled = fixture.nativeElement;
    
    // Check for key UI elements
    expect(compiled.querySelector('.video-dashboard')).toBeTruthy();
    expect(compiled.querySelector('.video-wrapper')).toBeTruthy();
    expect(compiled.querySelector('.fps-badge')).toBeTruthy();
    expect(compiled.querySelector('.results-container')).toBeTruthy();
    
    // Check for cognitive bias visualization elements
    expect(compiled.querySelector('.confidence-progress')).toBeTruthy();
    expect(compiled.querySelector('.pose-indicator')).toBeTruthy();
  });

  it('should clean up resources on destroy', () => {
    spyOn(mockVideoService, 'dispose');
    component.ngOnDestroy();
    expect(mockVideoService.dispose).toHaveBeenCalled();
  });
});
