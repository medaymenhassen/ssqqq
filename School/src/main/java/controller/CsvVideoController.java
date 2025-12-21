package com.auth.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.List;
import java.util.ArrayList;
import java.util.Arrays;
import com.auth.model.User;
import com.auth.service.UserService;

@RestController
@RequestMapping("/springboot/csv")
@CrossOrigin(origins = {"http://localhost:4200", "https://cognitiex.com"})
public class CsvVideoController {
    
    @Autowired
    private UserService userService;

    // Directory to store uploaded CSV files and generated videos
    private static final String UPLOAD_DIR = "./src/main/resources/static/uploads/";
    
    // Constants for different data types
    private static final String POSE_DATA_TYPE = "pose";
    private static final String FACE_DATA_TYPE = "face";
    private static final String HANDS_DATA_TYPE = "hands";
    
    /**
     * Upload a video file
     */
    @PostMapping("/upload-video")
    public ResponseEntity<?> uploadVideo(
            @RequestParam("file") MultipartFile file,
            @RequestParam(required = false) Long userId) {
        try {
            // Validate inputs
            if (file == null || file.isEmpty()) {
                return ResponseEntity.badRequest().body("File is required");
            }
            
            // Get authenticated user if userId not provided
            if (userId == null) {
                Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
                if (authentication != null && authentication.getPrincipal() instanceof String) {
                    String email = (String) authentication.getPrincipal();
                    User user = userService.findByEmail(email).orElse(null);
                    if (user != null) {
                        userId = user.getId();
                    }
                }
            }
            
            // Validate user
            if (userId == null) {
                return ResponseEntity.badRequest().body("User ID is required");
            }
            
            // Create upload directory if it doesn't exist
            File uploadDir = new File(UPLOAD_DIR);
            if (!uploadDir.exists()) {
                uploadDir.mkdirs();
            }
            
            // Save file
            String originalFileName = file.getOriginalFilename();
            String fileExtension = "";
            if (originalFileName != null && originalFileName.contains(".")) {
                fileExtension = originalFileName.substring(originalFileName.lastIndexOf("."));
            }
            String videoFileName = UUID.randomUUID().toString() + fileExtension;
            Path filePath = Paths.get(UPLOAD_DIR, videoFileName);
            
            Files.write(filePath, file.getBytes());
            
            // Get file information
            long fileSize = file.getSize();
            String contentType = file.getContentType();
            
            // Prepare response
            Map<String, Object> response = new HashMap<>();
            response.put("status", "success");
            response.put("message", "Video uploaded successfully");
            response.put("videoUrl", "/uploads/" + videoFileName);
            response.put("fileName", videoFileName);
            response.put("fileSize", fileSize);
            response.put("contentType", contentType);
            response.put("userId", userId);
            response.put("uploadedAt", java.time.LocalDateTime.now());
            response.put("processingTimestamp", java.time.LocalDateTime.now());
            
            return ResponseEntity.ok(response);
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error uploading file: " + e.getMessage());
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Unexpected error: " + e.getMessage());
        }
    }
    
    /**
     * List all uploaded files
     */
    @GetMapping("/list-files")
    public ResponseEntity<?> listUploadedFiles() {
        try {
            File uploadDir = new File(UPLOAD_DIR);
            if (!uploadDir.exists()) {
                return ResponseEntity.ok(new HashMap<String, Object>() {{
                    put("files", new ArrayList<>());
                    put("message", "Upload directory does not exist");
                }});
            }
            
            File[] files = uploadDir.listFiles();
            List<Map<String, Object>> fileList = new ArrayList<>();
            
            if (files != null) {
                for (File file : files) {
                    if (file.isFile()) {
                        Map<String, Object> fileInfo = new HashMap<>();
                        fileInfo.put("name", file.getName());
                        fileInfo.put("size", file.length());
                        fileInfo.put("lastModified", file.lastModified());
                        fileInfo.put("url", "/uploads/" + file.getName());
                        fileList.add(fileInfo);
                    }
                }
            }
            
            Map<String, Object> response = new HashMap<>();
            response.put("files", fileList);
            response.put("count", fileList.size());
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error listing files: " + e.getMessage());
        }
    }
    
    /**
     * Delete an uploaded file
     */
    @DeleteMapping("/delete-file/{filename}")
    public ResponseEntity<?> deleteUploadedFile(@PathVariable String filename) {
        try {
            if (filename == null || filename.trim().isEmpty()) {
                return ResponseEntity.badRequest().body("Filename is required");
            }
            
            Path filePath = Paths.get(UPLOAD_DIR, filename);
            File file = filePath.toFile();
            
            if (!file.exists()) {
                return ResponseEntity.notFound().build();
            }
            
            if (file.delete()) {
                Map<String, Object> response = new HashMap<>();
                response.put("status", "success");
                response.put("message", "File deleted successfully");
                response.put("filename", filename);
                
                return ResponseEntity.ok(response);
            } else {
                return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                        .body("Failed to delete file");
            }
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error deleting file: " + e.getMessage());
        }
    }
    
    /**
     * Get detailed information about a specific video
     */
    @GetMapping("/video-info/{filename:.+}")
    public ResponseEntity<?> getVideoInfo(@PathVariable String filename) {
        try {
            if (filename == null || filename.trim().isEmpty()) {
                return ResponseEntity.badRequest().body("Filename is required");
            }
            
            Path filePath = Paths.get(UPLOAD_DIR, filename);
            File file = filePath.toFile();
            
            if (!file.exists()) {
                return ResponseEntity.notFound().build();
            }
            
            // Get file information
            Map<String, Object> fileInfo = new HashMap<>();
            fileInfo.put("name", file.getName());
            fileInfo.put("size", file.length());
            fileInfo.put("lastModified", file.lastModified());
            fileInfo.put("url", "/uploads/" + file.getName());
            fileInfo.put("exists", true);
            
            // If it's a CSV file, analyze it
            if (filename.toLowerCase().endsWith(".csv")) {
                try {
                    String content = new String(Files.readAllBytes(filePath));
                    List<String> detectionTimes = analyzePoseDetectionTimes(content);
                    fileInfo.put("poseDetectionTimes", detectionTimes);
                    fileInfo.put("rowCount", content.split("\n").length - 1);
                } catch (IOException e) {
                    fileInfo.put("analysisError", "Could not analyze CSV file: " + e.getMessage());
                }
            }
            
            return ResponseEntity.ok(fileInfo);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error getting video info: " + e.getMessage());
        }
    }
    
    /**
     * Create a video from CSV data
     * This implementation processes the CSV data to create a structured representation
     */
    @PostMapping("/create-video")
    public ResponseEntity<?> createVideoFromCSV(
            @RequestParam("file") MultipartFile file,
            @RequestParam(required = false) Long userId,
            @RequestParam String videoName) {
        try {
            // Validate inputs
            if (file == null || file.isEmpty()) {
                return ResponseEntity.badRequest().body("File is required");
            }
            
            // Get authenticated user if userId not provided
            if (userId == null) {
                Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
                if (authentication != null && authentication.getPrincipal() instanceof String) {
                    String email = (String) authentication.getPrincipal();
                    User user = userService.findByEmail(email).orElse(null);
                    if (user != null) {
                        userId = user.getId();
                    }
                }
            }
            
            // Validate user
            if (userId == null) {
                return ResponseEntity.badRequest().body("User ID is required");
            }
            
            if (videoName == null || videoName.trim().isEmpty()) {
                return ResponseEntity.badRequest().body("Video name is required");
            }
            
            // Create upload directory if it doesn't exist
            File uploadDir = new File(UPLOAD_DIR);
            if (!uploadDir.exists()) {
                uploadDir.mkdirs();
            }
            
            // Read CSV content
            String csvContent = new String(file.getBytes());
            
            // Save CSV file
            String csvFileName = UUID.randomUUID().toString() + ".csv";
            Path csvFilePath = Paths.get(UPLOAD_DIR, csvFileName);
            Files.write(csvFilePath, csvContent.getBytes());
            
            // Generate video file name
            String videoFileName = videoName.endsWith(".mp4") ? videoName : videoName + ".mp4";
            Path videoPath = Paths.get(UPLOAD_DIR, videoFileName);
            
            // Process CSV and create video representation
            createVideoFromCsvData(videoPath, csvContent);
            
            // Analyze CSV data to find when poses were detected
            List<String> poseDetectionTimes = analyzePoseDetectionTimes(csvContent);
            
            // Prepare response
            Map<String, Object> response = new HashMap<>();
            response.put("status", "success");
            response.put("message", "Video created successfully from CSV data");
            response.put("videoUrl", "/uploads/" + videoFileName);
            response.put("csvProcessed", csvFileName);
            response.put("userId", userId);
            response.put("processedRows", csvContent.split("\n").length - 1); // Subtract 1 for header
            response.put("poseDetectionTimes", poseDetectionTimes);
            response.put("processingTimestamp", java.time.LocalDateTime.now());
            
            return ResponseEntity.ok(response);
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error processing file: " + e.getMessage());
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Unexpected error: " + e.getMessage());
        }
    }
    
    /**
     * Create a video from combined CSV data containing pose, face, and hands data
     */
    @PostMapping("/create-combined-video")
    public ResponseEntity<?> createCombinedVideoFromCSV(
            @RequestParam("file") MultipartFile file,
            @RequestParam(required = false) Long userId,
            @RequestParam String videoName) {
        try {
            // Validate inputs
            if (file == null || file.isEmpty()) {
                return ResponseEntity.badRequest().body("File is required");
            }
            
            // Get authenticated user if userId not provided
            if (userId == null) {
                Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
                if (authentication != null && authentication.getPrincipal() instanceof String) {
                    String email = (String) authentication.getPrincipal();
                    User user = userService.findByEmail(email).orElse(null);
                    if (user != null) {
                        userId = user.getId();
                    }
                }
            }
            
            // Validate user
            if (userId == null) {
                return ResponseEntity.badRequest().body("User ID is required");
            }
            
            if (videoName == null || videoName.trim().isEmpty()) {
                return ResponseEntity.badRequest().body("Video name is required");
            }
            
            // Create upload directory if it doesn't exist
            File uploadDir = new File(UPLOAD_DIR);
            if (!uploadDir.exists()) {
                uploadDir.mkdirs();
            }
            
            // Read CSV content
            String csvContent = new String(file.getBytes());
            
            // Save CSV file
            String csvFileName = UUID.randomUUID().toString() + ".csv";
            Path csvFilePath = Paths.get(UPLOAD_DIR, csvFileName);
            Files.write(csvFilePath, csvContent.getBytes());
            
            // Generate video file name
            String videoFileName = videoName.endsWith(".mp4") ? videoName : videoName + ".mp4";
            Path videoPath = Paths.get(UPLOAD_DIR, videoFileName);
            
            // Process combined CSV and create video representation
            createCombinedVideoFromCsvData(videoPath, csvContent);
            
            // Analyze CSV data to find when poses were detected
            List<String> poseDetectionTimes = analyzePoseDetectionTimes(csvContent);
            
            // Prepare response
            Map<String, Object> response = new HashMap<>();
            response.put("status", "success");
            response.put("message", "Combined video created successfully from CSV data");
            response.put("videoUrl", "/uploads/" + videoFileName);
            response.put("csvProcessed", csvFileName);
            response.put("userId", userId);
            response.put("processedRows", csvContent.split("\n").length - 1); // Subtract 1 for header
            response.put("poseDetectionTimes", poseDetectionTimes);
            response.put("processingTimestamp", java.time.LocalDateTime.now());
            
            return ResponseEntity.ok(response);
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error processing file: " + e.getMessage());
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Unexpected error: " + e.getMessage());
        }
    }
    
    /**
     * Analyze CSV data to find when poses were detected
     * @param csvContent The CSV content to analyze
     * @return List of timestamps when poses were detected
     */
    private List<String> analyzePoseDetectionTimes(String csvContent) {
        List<String> detectionTimes = new ArrayList<>();
        
        if (csvContent == null || csvContent.isEmpty()) {
            return detectionTimes;
        }
        
        String[] lines = csvContent.split("\n");
        if (lines.length <= 1) {
            return detectionTimes;
        }
        
        // Parse headers to find timestamp column
        String[] headers = lines[0].split(",");
        int timestampIndex = -1;
        int confidenceIndex = -1;
        
        for (int i = 0; i < headers.length; i++) {
            String header = headers[i].toLowerCase().trim();
            if (header.contains("timestamp")) {
                timestampIndex = i;
            } else if (header.contains("confidence")) {
                confidenceIndex = i;
            }
        }
        
        // If we can't find a timestamp column, use line numbers
        if (timestampIndex == -1) {
            for (int i = 1; i < Math.min(lines.length, 101); i++) { // Limit to 100 rows
                detectionTimes.add("Frame " + (i - 1));
            }
            return detectionTimes;
        }
        
        // Analyze each row for pose detections
        for (int i = 1; i < Math.min(lines.length, 101); i++) { // Limit to 100 rows
            String[] values = lines[i].split(",");
            if (values.length > timestampIndex) {
                String timestamp = values[timestampIndex].trim();
                
                // If we have confidence data, check if it's above threshold
                if (confidenceIndex != -1 && values.length > confidenceIndex) {
                    try {
                        double confidence = Double.parseDouble(values[confidenceIndex].trim());
                        if (confidence > 0.5) { // Threshold for significant detection
                            detectionTimes.add(timestamp);
                        }
                    } catch (NumberFormatException e) {
                        // If we can't parse confidence, just add the timestamp
                        detectionTimes.add(timestamp);
                    }
                } else {
                    // No confidence data, just add the timestamp
                    detectionTimes.add(timestamp);
                }
            }
        }
        
        return detectionTimes;
    }
    
    /**
     * Analyze frame data to extract detailed information about each frame
     * @param lines The CSV lines to analyze
     * @return List of frame analysis data
     */
    private List<Map<String, Object>> analyzeFrameData(String[] lines) {
        List<Map<String, Object>> frameAnalysis = new ArrayList<>();
        
        if (lines == null || lines.length <= 1) {
            return frameAnalysis;
        }
        
        // Parse headers to find important columns
        String[] headers = lines[0].split(",");
        int timestampIndex = -1;
        int confidenceIndex = -1;
        int gestureIndex = -1;
        int handIndex = -1;
        
        for (int i = 0; i < headers.length; i++) {
            String header = headers[i].toLowerCase().trim();
            if (header.contains("timestamp")) {
                timestampIndex = i;
            } else if (header.contains("confidence")) {
                confidenceIndex = i;
            } else if (header.contains("gesture")) {
                gestureIndex = i;
            } else if (header.contains("hand")) {
                handIndex = i;
            }
        }
        
        // Analyze each frame
        for (int i = 1; i < Math.min(lines.length, 101); i++) { // Limit to 100 frames
            Map<String, Object> frame = new HashMap<>();
            frame.put("frameIndex", i - 1);
            
            String[] values = lines[i].split(",");
            
            // Get timestamp
            String timestamp = "Unknown";
            if (timestampIndex != -1 && values.length > timestampIndex) {
                timestamp = values[timestampIndex].trim();
            } else {
                timestamp = "Frame " + (i - 1);
            }
            frame.put("timestamp", timestamp);
            
            // Count detected objects
            int detectedObjects = 0;
            
            // Check for pose/hand detections based on confidence
            if (confidenceIndex != -1 && values.length > confidenceIndex) {
                try {
                    double confidence = Double.parseDouble(values[confidenceIndex].trim());
                    if (confidence > 0.5) { // Threshold for significant detection
                        detectedObjects++;
                    }
                } catch (NumberFormatException e) {
                    // Ignore parsing errors
                }
            }
            
            // Check for gestures
            if (gestureIndex != -1 && values.length > gestureIndex) {
                String gesture = values[gestureIndex].trim();
                if (!gesture.isEmpty() && !"unknown".equalsIgnoreCase(gesture)) {
                    detectedObjects++;
                }
            }
            
            frame.put("detectedObjects", detectedObjects);
            frameAnalysis.add(frame);
        }
        
        return frameAnalysis;
    }
    
    /**
     * Create a structured video representation from CSV data
     * This creates a JSON-like structure representing the video data
     */
    private void createVideoFromCsvData(Path videoPath, String csvContent) throws IOException {
        // Parse CSV data to create a structured video representation
        String[] lines = csvContent.split("\n");
        
        // Determine data type from headers
        String dataType = detectDataType(lines.length > 0 ? lines[0] : "");
        
        // Analyze pose detection information
        List<Map<String, Object>> frameAnalysis = analyzeFrameData(lines);
        
        try (FileWriter writer = new FileWriter(videoPath.toFile())) {
            writer.write("{\n");
            writer.write("  \"videoMetadata\": {\n");
            writer.write("    \"generatedAt\": \"" + java.time.LocalDateTime.now() + "\",\n");
            writer.write("    \"rowCount\": " + (lines.length - 1) + ",\n"); // Subtract 1 for header
            writer.write("    \"dataType\": \"" + dataType + "\",\n");
            writer.write("    \"frameCount\": " + Math.max(0, lines.length - 1) + "\n");
            writer.write("  },\n");
            
            if (lines.length > 0) {
                writer.write("  \"header\": [\n");
                String[] headers = lines[0].split(",");
                for (int i = 0; i < headers.length; i++) {
                    writer.write("    \"" + headers[i].trim() + "\"" + (i < headers.length - 1 ? "," : "") + "\n");
                }
                writer.write("  ],\n");
                
                writer.write("  \"dataFrames\": [\n");
                for (int i = 1; i < Math.min(lines.length, 101); i++) { // Limit to 100 rows for demo
                    writer.write("    {\n");
                    writer.write("      \"frameIndex\": " + (i - 1) + ",\n");
                    String[] values = lines[i].split(",");
                    for (int j = 0; j < Math.min(headers.length, values.length); j++) {
                        writer.write("      \"" + headers[j].trim() + "\": \"" + values[j].trim() + "\"" + 
                                   (j < Math.min(headers.length, values.length) - 1 ? "," : "") + "\n");
                    }
                    writer.write("    }" + (i < Math.min(lines.length, 101) - 1 ? "," : "") + "\n");
                }
                writer.write("  ],\n");
                
                // Add frame analysis
                writer.write("  \"frameAnalysis\": [\n");
                for (int i = 0; i < Math.min(frameAnalysis.size(), 100); i++) { // Limit to 100 frames
                    Map<String, Object> frame = frameAnalysis.get(i);
                    writer.write("    {\n");
                    writer.write("      \"frameIndex\": " + frame.get("frameIndex") + ",\n");
                    writer.write("      \"timestamp\": \"" + frame.get("timestamp") + "\",\n");
                    writer.write("      \"detectedObjects\": " + frame.get("detectedObjects") + "\n");
                    writer.write("    }" + (i < Math.min(frameAnalysis.size(), 100) - 1 ? "," : "") + "\n");
                }
                writer.write("  ]\n");
            }
            
            writer.write("}\n");
        }
    }
    
    /**
     * Create a structured video representation from combined CSV data
     * This creates a JSON-like structure representing all movement data
     */
    private void createCombinedVideoFromCsvData(Path videoPath, String csvContent) throws IOException {
        // Parse CSV data to create a structured video representation
        String[] lines = csvContent.split("\n");
        
        // Analyze pose detection information
        List<Map<String, Object>> frameAnalysis = analyzeFrameData(lines);
        
        try (FileWriter writer = new FileWriter(videoPath.toFile())) {
            writer.write("{\n");
            writer.write("  \"videoMetadata\": {\n");
            writer.write("    \"generatedAt\": \"" + java.time.LocalDateTime.now() + "\",\n");
            writer.write("    \"rowCount\": " + (lines.length - 1) + ",\n"); // Subtract 1 for header
            writer.write("    \"dataType\": \"combined_movement_analysis\",\n");
            writer.write("    \"frameCount\": " + Math.max(0, lines.length - 1) + "\n");
            writer.write("  },\n");
            
            if (lines.length > 0) {
                writer.write("  \"header\": [\n");
                String[] headers = lines[0].split(",");
                for (int i = 0; i < headers.length; i++) {
                    writer.write("    \"" + headers[i].trim() + "\"" + (i < headers.length - 1 ? "," : "") + "\n");
                }
                writer.write("  ],\n");
                
                writer.write("  \"dataFrames\": [\n");
                for (int i = 1; i < Math.min(lines.length, 101); i++) { // Limit to 100 rows for demo
                    writer.write("    {\n");
                    writer.write("      \"frameIndex\": " + (i - 1) + ",\n");
                    String[] values = lines[i].split(",");
                    for (int j = 0; j < Math.min(headers.length, values.length); j++) {
                        writer.write("      \"" + headers[j].trim() + "\": \"" + values[j].trim() + "\"" + 
                                   (j < Math.min(headers.length, values.length) - 1 ? "," : "") + "\n");
                    }
                    writer.write("    }" + (i < Math.min(lines.length, 101) - 1 ? "," : "") + "\n");
                }
                writer.write("  ],\n");
                
                // Add frame analysis
                writer.write("  \"frameAnalysis\": [\n");
                for (int i = 0; i < Math.min(frameAnalysis.size(), 100); i++) { // Limit to 100 frames
                    Map<String, Object> frame = frameAnalysis.get(i);
                    writer.write("    {\n");
                    writer.write("      \"frameIndex\": " + frame.get("frameIndex") + ",\n");
                    writer.write("      \"timestamp\": \"" + frame.get("timestamp") + "\",\n");
                    writer.write("      \"detectedObjects\": " + frame.get("detectedObjects") + "\n");
                    writer.write("    }" + (i < Math.min(frameAnalysis.size(), 100) - 1 ? "," : "") + "\n");
                }
                writer.write("  ]\n");
            }
            
            writer.write("}\n");
        }
    }
    
    /**
     * Detect data type from CSV headers
     */
    private String detectDataType(String headerLine) {
        if (headerLine == null || headerLine.isEmpty()) {
            return "unknown";
        }
        
        String[] headers = headerLine.toLowerCase().split(",");
        
        // Check for pose data indicators
        boolean hasPoseIndicators = Arrays.stream(headers)
                .anyMatch(header -> header.contains("pose") || header.contains("landmark"));
                
        // Check for face data indicators
        boolean hasFaceIndicators = Arrays.stream(headers)
                .anyMatch(header -> header.contains("face"));
                
        // Check for hands data indicators
        boolean hasHandsIndicators = Arrays.stream(headers)
                .anyMatch(header -> header.contains("hand") || header.contains("wrist") || header.contains("finger"));
                
        if (hasPoseIndicators && hasFaceIndicators && hasHandsIndicators) {
            return "combined";
        } else if (hasPoseIndicators) {
            return POSE_DATA_TYPE;
        } else if (hasFaceIndicators) {
            return FACE_DATA_TYPE;
        } else if (hasHandsIndicators) {
            return HANDS_DATA_TYPE;
        } else {
            return "unknown";
        }
    }
}