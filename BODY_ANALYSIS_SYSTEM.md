# Body Analysis System Documentation

## Overview

The Body Analysis System is designed to process video content for human body movement analysis using MediaPipe and integrate with the backend for data storage and processing.

## System Architecture

### Frontend Components

1. **VideoService** (`src/app/video.service.ts`)
   - Integrates MediaPipe Tasks API for real-time body tracking
   - Processes pose, face, and hand landmarks
   - Converts raw MediaPipe data to structured format using Kalidokit
   - Provides real-time analysis data through Observables

2. **ImageBodyAnalysisService** (`src/app/services/image-body-analysis.service.ts`)
   - Simulates body analysis from static images
   - Generates CSV data for pose, face, and hand movements
   - Creates combined CSV for video generation

### Backend Components

1. **DocumentController** (`School/src/main/java/controller/DocumentController.java`)
   - Provides `/upload-for-body-analysis` endpoint for video uploads
   - Validates video files and associates them with users
   - Stores documents for body analysis processing

2. **DocumentService** (`School/src/main/java/service/DocumentService.java`)
   - Implements `uploadDocumentForBodyAnalysis` method
   - Handles file storage and document metadata creation
   - Associates videos with users for tracking

3. **CsvVideoController** (`School/src/main/java/controller/CsvVideoController.java`)
   - Provides endpoints for CSV processing and video generation
   - Handles `/create-combined-video` for generating videos from movement data
   - Manages file uploads and processing

## Workflow

### 1. Real-time Video Analysis

1. User accesses the video component in the Angular application
2. MediaPipe initializes pose, face, and hand detectors
3. Webcam feed is processed frame-by-frame
4. Landmark data is converted to structured format
5. Analysis data is displayed in real-time
6. Users can export data as CSV files

### 2. Video Upload for Analysis

1. User records or selects a video file
2. Video is uploaded to `/api/documents/upload-for-body-analysis`
3. Backend validates file type and user association
4. Video is stored in the uploads directory
5. Document record is created in the database

### 3. CSV Data Processing

1. Pose, face, and hand data is exported as CSV
2. CSV files are uploaded to backend
3. Backend processes CSV data to generate video representations
4. Combined movement data can be used to create analysis videos

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login

### Document Management
- `POST /api/documents/upload-for-body-analysis` - Upload video for body analysis
- `GET /api/documents/user/{userId}` - Get user's documents
- `GET /api/documents/{documentId}/download` - Download document

### CSV Processing
- `POST /springboot/csv/create-combined-video` - Create video from combined CSV data
- `POST /springboot/csv/upload-video` - Upload video files
- `GET /springboot/csv/list-files` - List uploaded files

## Data Formats

### Pose Data
```csv
Timestamp,Pose Confidence,Head X,Head Y,Head Z,Head Confidence,...
```

### Face Data
```csv
Timestamp,Face Confidence,Mouth Open,Eye Blink Left,Eye Blink Right,...
```

### Hands Data
```csv
Timestamp,Hand,Gesture,Confidence,Landmark Count
```

## Testing

### Python Test Scripts

1. `complete_body_analysis_test.py` - Complete pipeline test
2. `body_analysis_simple_test.py` - Simplified body analysis test
3. `test_image_body_analysis.py` - Image-based analysis test
4. `test_video_generation.py` - Video generation test

### Batch Files
- `run_body_analysis_test.bat` - Run complete body analysis test

## Requirements

### Frontend
- Angular 15+
- MediaPipe Tasks API
- Kalidokit for data conversion
- OpenCV for image processing

### Backend
- Java Spring Boot
- Maven for dependency management
- File storage for uploaded videos

### Python Testing
- Python 3.6+
- OpenCV
- MediaPipe
- Requests library
- NumPy

## Troubleshooting

### Common Issues

1. **MediaPipe Initialization Failures**
   - Check internet connection for model downloads
   - Verify browser compatibility
   - Ensure HTTPS in production environments

2. **Video Upload Errors**
   - Check file size limits
   - Verify video format support (MP4 recommended)
   - Confirm user authentication

3. **CSV Processing Failures**
   - Validate CSV format matches expected headers
   - Check file encoding
   - Ensure sufficient memory for large files

### Debugging Steps

1. Check browser console for JavaScript errors
2. Monitor network requests in developer tools
3. Review backend logs for processing errors
4. Validate file permissions for upload directory
5. Test endpoints with Postman or curl

## Future Enhancements

1. **Advanced Analysis**
   - Motion pattern recognition
   - Anomaly detection
   - Performance metrics

2. **Enhanced Visualization**
   - 3D skeleton visualization
   - Heatmap generation
   - Comparative analysis

3. **Integration Features**
   - Machine learning model training
   - Automated report generation
   - Export to various formats (JSON, XML, etc.)