export interface DataRecord {
  id?: number;
  userId: number;
  imageData?: string; // Base64 encoded image
  videoUrl?: string;  // URL to 30-second video segment
  videoBlob?: Blob;   // Actual video blob data
  jsonData?: any;     // JSON text data (Q&A, etc.)
  timestamp: Date;
  movementDetected: boolean;
  position?: {
    x: number;
    y: number;
  };
  velocity?: number;
  direction?: number;
  confidence?: number;
}