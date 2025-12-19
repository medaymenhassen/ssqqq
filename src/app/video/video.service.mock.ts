import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, of } from 'rxjs';

export interface BodyAnalysis {
  pose: any;
  face: any;
  hands: {
    left: any;
    right: any;
  };
  isAnalyzing: boolean;
}

@Injectable()
export class MockVideoService {
  private bodyAnalysisSubject = new BehaviorSubject<BodyAnalysis>({
    pose: null,
    face: null,
    hands: { left: null, right: null },
    isAnalyzing: false
  });

  public bodyAnalysis$ = this.bodyAnalysisSubject.asObservable();

  initializeMediaPipe(): Promise<void> {
    return Promise.resolve();
  }

  analyzeFrame(videoElement: HTMLVideoElement): Promise<void> {
    return Promise.resolve();
  }

  getCurrentAnalysis(): BodyAnalysis {
    return this.bodyAnalysisSubject.value;
  }

  dispose(): void {}
}