export interface DataRecord {
  id?: number;
  userId: number;
  imageData?: string; // Base64 encoded image
  videoUrl?: string;  // URL to 30-second video segment
  jsonData?: any;     // JSON text data (Q&A, etc.)
  timestamp: Date;
  movementDetected: boolean;
}