import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

// Modern MediaPipe Tasks API
import * as Kalidokit from 'kalidokit';
import {
  PoseLandmarker,
  FaceLandmarker,
  HandLandmarker,
  FilesetResolver,
  HolisticLandmarker,
  DrawingUtils,
  Landmark
} from '@mediapipe/tasks-vision';

// For drawing utilities
import { drawConnectors, drawLandmarks } from '@mediapipe/drawing_utils';

import { Camera } from '@mediapipe/camera_utils';

export interface PoseData {
  [key: string]: {
    position?: { x: number; y: number; z?: number };
    rotation?: { x: number; y: number; z: number; w?: number };
    confidence?: number;
  };
}

export interface FaceData {
  Head?: {
    position?: { x: number; y: number; z: number };
    rotation?: { x: number; y: number; z: number };
  };
  mouth_open?: number;
  eye_blink_left?: number;
  eye_blink_right?: number;
  eye_look_left?: number;
  eye_look_right?: number;
}

export interface HandData {
  landmarks?: any[];
  handedness?: string;
  gesture?: string;
}

export interface BodyAnalysis {
  pose: PoseData | null;
  face: FaceData | null;
  hands: {
    left: HandData | null;
    right: HandData | null;
  };
  isAnalyzing: boolean;
  poseConfidence?: number;
  faceConfidence?: number;
  handsDetected?: { left: boolean; right: boolean };
  bodyMetrics?: {
    posture: string;
    faceExpression: string;
    leftGesture: string;
    rightGesture: string;
  };
}

@Injectable({
  providedIn: 'root'
})
export class VideoService {
  private bodyAnalysisSubject = new BehaviorSubject<BodyAnalysis>({
    pose: null,
    face: null,
    hands: { left: null, right: null },
    isAnalyzing: false,
    poseConfidence: 0,
    faceConfidence: 0,
    handsDetected: { left: false, right: false },
    bodyMetrics: {
      posture: 'Neutre',
      faceExpression: 'Neutre',
      leftGesture: 'Aucun',
      rightGesture: 'Aucun'
    }
  });

  public bodyAnalysis$: Observable<BodyAnalysis> = this.bodyAnalysisSubject.asObservable();

  private holistic: HolisticLandmarker | null = null;
  private poseDetector: PoseLandmarker | null = null;
  private faceDetector: FaceLandmarker | null = null;
  private handDetector: HandLandmarker | null = null;
  private mpCamera: Camera | null = null;
  private kalidokit = Kalidokit;

  constructor() {}

  async initializeMediaPipe(): Promise<void> {
    
    // Only initialize MediaPipe in browser environment
    if (typeof window === 'undefined') {
      return;
    }
    
    if (this.holistic) return;

    try {
      // Use the latest version and a more reliable model path
      const filesetResolver = await FilesetResolver.forVisionTasks(
        'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm'
      );

      // Skip holistic and go directly to individual detectors
      await this.initializeIndividualDetectors(filesetResolver);
    } catch (error) {
    }
  }

  private async initializeIndividualDetectors(filesetResolver: any): Promise<void> {
    try {
      // Initialize pose detector
      this.poseDetector = await PoseLandmarker.createFromOptions(filesetResolver, {
        baseOptions: {
          modelAssetPath: 'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/latest/pose_landmarker_heavy.task',
        },
        runningMode: 'VIDEO',
        numPoses: 1
      });

      // Initialize face detector
      this.faceDetector = await FaceLandmarker.createFromOptions(filesetResolver, {
        baseOptions: {
          modelAssetPath: 'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task',
        },
        runningMode: 'VIDEO'
      });

      // Initialize hand detectors
      this.handDetector = await HandLandmarker.createFromOptions(filesetResolver, {
        baseOptions: {
          modelAssetPath: 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task',
        },
        runningMode: 'VIDEO',
        numHands: 2
      });

    } catch (error) {
      // Even if individual detectors fail, we can still notify the UI
      this.updateAnalysis({ 
        isAnalyzing: false, 
        poseConfidence: 0, 
        faceConfidence: 0, 
        handsDetected: { left: false, right: false } 
      });
    }
  }

  async setupHolistic(videoElement: HTMLVideoElement): Promise<void> {
    
    // Only setup in browser environment
    if (typeof window === 'undefined') {
      return;
    }
    
    try {
      if (!this.poseDetector && !this.faceDetector && !this.handDetector) {
        await this.initializeMediaPipe();
      }

      // Check if any detector is available
      if (!this.poseDetector && !this.faceDetector && !this.handDetector) {
        throw new Error('Aucun détecteur initialisé');
      }

      // Start camera
      this.mpCamera = new Camera(videoElement, {
        onFrame: async () => {
          if ((this.poseDetector || this.faceDetector || this.handDetector) && 
              videoElement.videoWidth > 0 && videoElement.videoHeight > 0) {
            try {
              // Use individual detectors
              await this.detectWithIndividualDetectors(videoElement);
            } catch (e) {
            }
          }
        },
        width: 1280,
        height: 720
      });

      this.mpCamera.start();
      console.log("Détecteurs démarrés !");
    } catch (error) {
      // Notify the UI that tracking is not available
      this.updateAnalysis({ 
        isAnalyzing: false, 
        poseConfidence: 0, 
        faceConfidence: 0, 
        handsDetected: { left: false, right: false } 
      });
    }
  }

  private async detectWithIndividualDetectors(videoElement: HTMLVideoElement): Promise<void> {
    const results: any = {};
    
    try {
      // Detect pose
      if (this.poseDetector) {
        const poseResults = await this.poseDetector.detectForVideo(videoElement, performance.now());
        if (poseResults.landmarks && poseResults.landmarks.length > 0) {
          results.poseLandmarks = poseResults.landmarks;
          results.poseWorldLandmarks = poseResults.worldLandmarks;
        }
      }
      
      // Detect face
      if (this.faceDetector) {
        const faceResults = await this.faceDetector.detectForVideo(videoElement, performance.now());
        if (faceResults.faceLandmarks && faceResults.faceLandmarks.length > 0) {
          results.faceLandmarks = faceResults.faceLandmarks;
        }
      }
      
      // Detect hands
      if (this.handDetector) {
        const handResults = await this.handDetector.detectForVideo(videoElement, performance.now());
        if (handResults.landmarks && handResults.landmarks.length > 0) {
          // Separate left and right hands based on x position
          handResults.landmarks.forEach((landmarks: any, index: number) => {
            if (handResults.handednesses && handResults.handednesses[index]) {
              const handedness = handResults.handednesses[index][0].categoryName;
              if (handedness === 'Left') {
                results.leftHandLandmarks = landmarks;
              } else if (handedness === 'Right') {
                results.rightHandLandmarks = landmarks;
              }
            }
          });
        }
      }
      
      this.processResults(results);
    } catch (error) {
      this.updateAnalysis({ isAnalyzing: false });
    }
  }

  private processResults(results: any): void {
    if (!results) {
      return;
    }

    try {
      this.updateAnalysis({ isAnalyzing: true });

      let poseData: PoseData | null = null;
      let poseConfidence = 0;
      let leftHand: HandData | null = null;
      let rightHand: HandData | null = null;
      let faceData: FaceData | null = null;
      let faceConfidence = 0;

      // Process pose
      if (results.poseLandmarks && results.poseLandmarks.length > 0) {
        poseData = this.convertPoseToKalidokit(results.poseLandmarks, results.poseWorldLandmarks);
        poseConfidence = this.calculatePoseConfidence(results.poseLandmarks);
      }

      // Process hands
      if (results.leftHandLandmarks) {
        leftHand = {
          landmarks: results.leftHandLandmarks,
          handedness: 'left',
          gesture: this.detectHandGesture(results.leftHandLandmarks)
        };

      }

      if (results.rightHandLandmarks) {
        rightHand = {
          landmarks: results.rightHandLandmarks,
          handedness: 'right',
          gesture: this.detectHandGesture(results.rightHandLandmarks)
        };
      }

      // Process face
      if (results.faceLandmarks && results.faceLandmarks.length > 0) {
        faceData = this.convertFaceToKalidokit(results.faceLandmarks);
        faceConfidence = this.calculateFaceConfidence(results.faceLandmarks);
      }

      const bodyMetrics = this.calculateBodyMetrics(poseData, faceData);

      this.updateAnalysis({
        pose: poseData,
        face: faceData,
        hands: {
          left: leftHand,
          right: rightHand
        },
        isAnalyzing: false,
        poseConfidence: poseConfidence,
        faceConfidence: faceConfidence,
        handsDetected: {
          left: leftHand !== null,
          right: rightHand !== null
        },
        bodyMetrics: bodyMetrics
      });
      

    } catch (error) {
      this.updateAnalysis({ isAnalyzing: false });
    }
  }

  private convertPoseToKalidokit(landmarks: any, worldLandmarks?: any): PoseData {
    try {
      // Validate inputs before processing
      if (!landmarks || !Array.isArray(landmarks) || landmarks.length === 0) {
        return {};
      }
      
      // Ensure all landmarks have required properties
      const validLandmarks = landmarks.map((landmark: any) => ({
        x: landmark?.x ?? 0,
        y: landmark?.y ?? 0,
        z: landmark?.z ?? 0,
        visibility: landmark?.visibility ?? landmark?.score ?? 0
      }));
      
      // Skip Kalidokit processing for now to avoid errors
      // const kalidokitPose = this.kalidokit.Pose.solve(validLandmarks, validLandmarks);

      const poseData: PoseData = {};

      const keyPoints = [
        'Head', 'Neck', 'Spine', 'Hips',
        'LeftShoulder', 'LeftElbow', 'LeftWrist',
        'RightShoulder', 'RightElbow', 'RightWrist',
        'LeftHip', 'LeftKnee', 'LeftAnkle',
        'RightHip', 'RightKnee', 'RightAnkle'
      ];

      keyPoints.forEach((keyPoint: string, index: number) => {
        if (validLandmarks[index]) {
          poseData[keyPoint] = {
            position: {
              x: validLandmarks[index].x,
              y: validLandmarks[index].y,
              z: validLandmarks[index].z
            },
            confidence: validLandmarks[index].visibility
          };
        }
      });
      
      return poseData;
    } catch (error) {
      // Return minimal pose data even if conversion fails
      return {};
    }
  }

  private convertFaceToKalidokit(faceLandmarks: any): FaceData {
    try {
      const kalidokitFace = this.kalidokit.Face.solve(faceLandmarks, { runtime: 'mediapipe' });

      const faceData: FaceData = {
        Head: {
          position: {
            x: faceLandmarks[0]?.x || 0,
            y: faceLandmarks[0]?.y || 0,
            z: faceLandmarks[0]?.z || 0
          }
        }
      };

      if (faceLandmarks.length > 0) {
        faceData.mouth_open = this.calculateMouthOpenness(faceLandmarks);
        faceData.eye_blink_left = this.detectEyeBlink(faceLandmarks, 'left');
        faceData.eye_blink_right = this.detectEyeBlink(faceLandmarks, 'right');
        faceData.eye_look_left = this.detectEyeGaze(faceLandmarks, 'left');
        faceData.eye_look_right = this.detectEyeGaze(faceLandmarks, 'right');
      }

      if (kalidokitFace) {
        Object.assign(faceData, kalidokitFace);
      }

      return faceData;
    } catch (error) {
      return {};
    }
  }

  private calculatePoseConfidence(landmarks: any): number {
    if (!landmarks || landmarks.length === 0) return 0;
    


    const keyIndices = [0, 11, 12, 13, 14, 15, 16];
    let totalConfidence = 0;
    let count = 0;

    keyIndices.forEach(idx => {
      if (landmarks[idx]) {
        // Check for different possible confidence properties
        const visibility = landmarks[idx].visibility ?? landmarks[idx].score ?? 0;
        totalConfidence += visibility;
        count++;

      }
    });

    const confidence = count > 0 ? Math.round((totalConfidence / count) * 100) : 0;
    return confidence;
  }

  private calculateFaceConfidence(faceLandmarks: any): number {
    if (!faceLandmarks || faceLandmarks.length === 0) return 0;

    let totalConfidence = 0;
    faceLandmarks.forEach((landmark: any) => {
      if (landmark?.z !== undefined) {
        totalConfidence += Math.max(0, 1 - Math.abs(landmark.z));
      }
    });

    const avgConfidence = totalConfidence / Math.max(1, faceLandmarks.length);
    return Math.round(avgConfidence * 100);
  }

  private detectHandGesture(landmarks: any): string {
    if (!landmarks || landmarks.length < 21) return 'Inconnu';

    if (this.isFist(landmarks)) return 'Poing';
    if (this.isVictory(landmarks)) return 'Victoire ✌️';
    if (this.isOK(landmarks)) return 'OK 👌';
    if (this.isThumbsUp(landmarks)) return 'Pouce 👍';
    if (this.isOpenHand(landmarks)) return 'Ouverte 🖐️';

    return 'Neutre';
  }

  private isFist(landmarks: any): boolean {
    if (!landmarks || landmarks.length < 21) return false;
    const tips = [landmarks[4], landmarks[8], landmarks[12], landmarks[16], landmarks[20]];
    const base = landmarks[9];
    return tips.every(tip => tip && base && Math.abs(tip.y - base.y) < 0.1);
  }

  private isVictory(landmarks: any): boolean {
    if (!landmarks || landmarks.length < 21) return false;
    const indexTip = landmarks[8];
    const middleTip = landmarks[12];
    const ringTip = landmarks[16];
    const pinkyTip = landmarks[20];
    const base = landmarks[9];

    return (indexTip && middleTip && ringTip && pinkyTip && base &&
      indexTip.y < base.y - 0.05 && middleTip.y < base.y - 0.05 &&
      ringTip.y > base.y - 0.05 && pinkyTip.y > base.y - 0.05);
  }

  private isOK(landmarks: any): boolean {
    if (!landmarks || landmarks.length < 21) return false;
    const thumbTip = landmarks[4];
    const indexTip = landmarks[8];
    if (!thumbTip || !indexTip) return false;
    const distance = Math.hypot(thumbTip.x - indexTip.x, thumbTip.y - indexTip.y);
    return distance < 0.1;
  }

  private isThumbsUp(landmarks: any): boolean {
    if (!landmarks || landmarks.length < 21) return false;
    const thumbTip = landmarks[4];
    const palmBase = landmarks[0];
    return thumbTip && palmBase && thumbTip.y < palmBase.y - 0.05;
  }

  private isOpenHand(landmarks: any): boolean {
    if (!landmarks || landmarks.length < 21) return false;
    const tips = [landmarks[4], landmarks[8], landmarks[12], landmarks[16], landmarks[20]];
    const base = landmarks[9];
    if (!base) return false;
    return tips.filter(tip => tip && tip.y < base.y - 0.05).length >= 4;
  }

  private calculateMouthOpenness(faceLandmarks: any): number {
    if (!faceLandmarks || faceLandmarks.length < 70) return 0;
    const topLip = faceLandmarks[61];
    const bottomLip = faceLandmarks[67];
    if (!topLip || !bottomLip) return 0;
    const distance = Math.hypot(topLip.x - bottomLip.x, topLip.y - bottomLip.y);
    // Make it more sensitive by increasing the multiplier
    return Math.min(100, Math.round(distance * 2000));
  }

  private detectEyeBlink(faceLandmarks: any, side: 'left' | 'right'): number {
    if (!faceLandmarks || faceLandmarks.length < 70) return 0;
    const startIdx = side === 'left' ? 159 : 386;
    const eyeLandmarks = faceLandmarks.slice(startIdx, startIdx + 10);

    if (eyeLandmarks.length === 0) return 0;

    let totalDistance = 0;
    let validPairs = 0;
    for (let i = 0; i < eyeLandmarks.length; i += 2) {
      if (eyeLandmarks[i] && eyeLandmarks[i + 1]) {
        const dist = Math.hypot(
          eyeLandmarks[i].x - eyeLandmarks[i + 1].x,
          eyeLandmarks[i].y - eyeLandmarks[i + 1].y
        );
        totalDistance += dist;
        validPairs++;
      }
    }

    if (validPairs === 0) return 0;
    
    const avgDistance = totalDistance / validPairs;
    // Make it more sensitive by adjusting the multiplier
    return Math.round(Math.max(0, 100 - avgDistance * 1000));
  }

  private detectEyeGaze(faceLandmarks: any, side: 'left' | 'right'): number {
    if (!faceLandmarks || faceLandmarks.length < 70) return 0;
    const pupilIdx = side === 'left' ? 473 : 468;

    if (faceLandmarks[pupilIdx]) {
      return faceLandmarks[pupilIdx].x * 200; // Increase sensitivity
    }
    return 0;
  }

  private calculateBodyMetrics(poseData: PoseData | null, faceData: FaceData | null) {
    let posture = 'Neutre';
    let faceExpression = 'Neutre';

    if (poseData) {
      const head = poseData['Head'];
      const leftShoulder = poseData['LeftShoulder'];
      const rightShoulder = poseData['RightShoulder'];

      if (head && leftShoulder && rightShoulder) {
        const shoulderAngle = Math.atan2(
          (rightShoulder.position?.y || 0) - (leftShoulder.position?.y || 0),
          (rightShoulder.position?.x || 0) - (leftShoulder.position?.x || 0)
        );

        if (Math.abs(shoulderAngle) > 0.2) posture = 'Penchée'; // Lower threshold
        else if (Math.abs(shoulderAngle) < 0.05) posture = 'Droite'; // Lower threshold
      }
    }

    if (faceData) {
      if (faceData.mouth_open && faceData.mouth_open > 20) { // Lower threshold
        faceExpression = 'Bouche ouverte';
      } else if ((faceData.eye_blink_left && faceData.eye_blink_left > 30) || 
                 (faceData.eye_blink_right && faceData.eye_blink_right > 30)) { // Lower threshold and check both eyes
        faceExpression = 'Clignotement';
      } else {
        faceExpression = 'Naturelle';
      }
    }

    return {
      posture,
      faceExpression,
      leftGesture: 'N/A',
      rightGesture: 'N/A'
    };
  }

  private updateAnalysis(partial: Partial<BodyAnalysis>): void {
    const current = this.bodyAnalysisSubject.value;
    this.bodyAnalysisSubject.next({
      ...current,
      ...partial
    });
  }

  getCurrentAnalysis(): BodyAnalysis {
    return this.bodyAnalysisSubject.value;
  }

  dispose(): void {
    if (this.mpCamera) {
      this.mpCamera.stop();
    }
    if (this.holistic) {
      this.holistic.close();
      this.holistic = null;
    }
  }
}