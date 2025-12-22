# 3D Project - Body Analytics Application

## Overview
This application provides real-time body tracking and analysis using MediaPipe technology. Users can access body tracking features by purchasing offers through the offer system.

## URLs and Routes

### Main Application Routes:
- **Body Analytics (Webcam Tracking)**: http://localhost:4200/bodyanalytics
- **Image Analysis**: http://localhost:4200/image-analysis
- **Available Offers**: http://localhost:4200/offers
- **Login**: http://localhost:4200/login
- **Register**: http://localhost:4200/register

### API Endpoints (Backend):
- **Offer Endpoints**:
  - GET `/api/offers` - Get all active offers
  - POST `/api/offers` - Create a new offer (Admin only)
  - POST `/api/offers/{offerId}/purchase?userId={userId}` - Purchase an offer
  - GET `/api/offers/user/{userId}/access` - Check if user has access

## How to Use

### 1. Starting the Application
1. Make sure both the frontend (Angular) and backend (Spring Boot) servers are running
2. Run one of the provided scripts to open the application in Google Chrome:
   - `open-chrome.bat` (Windows Batch)
   - `open-chrome.ps1` (PowerShell)

### 2. Accessing Body Tracking Features
1. Navigate to http://localhost:4200/bodyanalytics
2. Click the "Démarrer" button to start the webcam
3. Allow camera access when prompted by the browser
4. The system will begin tracking your body movements in real-time
5. Click "Arrêter" to stop the tracking and generate analysis data

### 3. Purchasing Offers
1. Navigate to http://localhost:4200/offers
2. Browse available offers
3. Click "Purchase" on any offer to gain access to course content
4. After purchasing, you'll have access to all course materials

### 4. Image Analysis
1. Navigate to http://localhost:4200/image-analysis
2. Upload an image containing a person
3. The system will analyze the body pose in the image
4. Results will be displayed with movement data

## Troubleshooting

### Webcam Issues
- Make sure no other applications are using your webcam
- Check browser permissions for camera access
- Try refreshing the page if the camera doesn't start

### Access Denied (403 Errors)
- Make sure you've purchased an offer to access course content
- Navigate to the Offers page to purchase an access pass

### Video Generation Issues
- Check that the backend server is running
- Verify that the uploads directory has write permissions
- Look at browser console logs for detailed error information

## Scripts
- `open-chrome.bat` - Opens the application in Google Chrome (Windows)
- `open-chrome.ps1` - Opens the application in Google Chrome (PowerShell)

## Components
- **VideoComponent**: Handles real-time webcam tracking and analysis
- **OfferListComponent**: Displays available offers and handles purchases
- **ImageAnalysisComponent**: Processes static images for body analysis
- **OfferService**: Manages communication with the backend offer API

## Services
- **VideoService**: Manages MediaPipe integration for body tracking
- **OfferService**: Handles offer-related API calls
- **AuthService**: Manages user authentication
- **AiService**: Handles AI-related data processing