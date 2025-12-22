# Image Body Analysis Feature

This feature allows analyzing body movements from static images as if they were video frames, simulating the same process used in the video component.

## Components

### Angular Service (`image-body-analysis.service.ts`)

The `ImageBodyAnalysisService` provides functionality to:
1. Simulate body analysis from images
2. Generate CSV data for pose, face, and hand movements
3. Create combined CSV data for video generation

### Python Test Script (`test_image_body_analysis.py`)

The Python test script demonstrates:
1. User registration and login
2. Simulated body analysis from images
3. CSV data generation
4. Backend interaction simulation

## How It Works

### 1. Image Analysis Simulation

Instead of processing live video frames, the service simulates analysis of the provided image:
- "Capture d'écran 2025-12-13 140829.jpg"
- Generates realistic pose, face, and hand data
- Provides confidence metrics similar to live analysis

### 2. Data Generation

The service generates three types of CSV data:
- **Pose Data**: Body landmark positions and confidence
- **Face Data**: Facial features and expressions
- **Hands Data**: Hand gestures and landmark positions

### 3. Video Creation

CSV data can be used to generate video files showing the analyzed movements over time.

## Running the Test

### Prerequisites
1. Python 3.6 or higher
2. Requests library (`pip install requests`)

### Execution
1. Run the batch script:
   ```
   run_image_analysis_test.bat
   ```

2. Or run directly with Python:
   ```
   python test_image_body_analysis.py
   ```

## Integration with Existing System

### Angular Integration
1. Import the `ImageBodyAnalysisService` in your component
2. Call `analyzeImageFromUrl()` with the image path
3. Subscribe to `analysis$` to receive results
4. Use the CSV generation methods to create data files

### Backend Integration
The Python script simulates calls to these endpoints:
- `/api/auth/register` - User registration
- `/api/auth/login` - User authentication
- `/api/upload/csv` - CSV data upload
- `/api/csv-to-video` - Video generation from CSV

## Future Enhancements

1. **Real Image Processing**: Integrate MediaPipe to process actual images
2. **Enhanced Analysis**: Add more detailed body part detection
3. **Batch Processing**: Process multiple images in sequence
4. **Comparison Features**: Compare movements across multiple images
5. **Storage Integration**: Save results to database

## Sample Output

The test produces output similar to:
```
🚀 Starting Image Body Analysis Workflow
==============================
📝 Registering user...
✅ User registered successfully
🔐 Logging in user...
✅ User logged in successfully
🔑 Access token obtained: eyJhbGciOiJIUzUxMiJ9...
🔍 Simulating body analysis from image...
📊 Body analysis completed
   Pose confidence: 87%
   Face confidence: 92%
   Hands detected: {'left': True, 'right': True}
📋 Generating CSV data...
✅ CSV data generated
📤 Simulating CSV data upload...
🎥 Simulating video creation from CSV...
🎉 Image Body Analysis Workflow Completed Successfully!
```

## Troubleshooting

### Common Issues
1. **Network Errors**: Ensure the backend server is running
2. **Authentication Failures**: Check user credentials
3. **Missing Dependencies**: Install required Python packages
4. **File Path Issues**: Verify image file exists

### Debugging Tips
1. Check browser console for JavaScript errors
2. Verify backend endpoints are accessible
3. Confirm database connectivity
4. Review CSV format matches backend expectations