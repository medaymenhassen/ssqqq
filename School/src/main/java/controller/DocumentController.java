package com.auth.controller;

import com.auth.model.Document;
import com.auth.model.User;
import com.auth.service.DocumentService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import jakarta.servlet.ServletOutputStream;
import jakarta.servlet.http.HttpServletResponse;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.util.List;
import java.util.Map;
import java.util.HashMap;
import org.springframework.http.HttpHeaders;

@RestController
@RequestMapping("/api/documents")
@CrossOrigin(origins = {"http://localhost:4200", "https://cognitiex.com"})
public class DocumentController {

    @Autowired
    private DocumentService documentService;

    @GetMapping
    public List<Document> getAllDocuments() {
        return documentService.getAllDocuments();
    }

    @GetMapping("/user/{userId}")
    public List<Document> getDocumentsByUser(@PathVariable Long userId) {
        return documentService.getDocumentsByUser(userId);
    }

    @GetMapping("/user-type/{userTypeId}")
    public List<Document> getDocumentsByUserType(@PathVariable Long userTypeId) {
        return documentService.getDocumentsByUserType(userTypeId);
    }

    @PostMapping("/upload")
    public ResponseEntity<?> uploadDocument(
            @RequestParam Long userId,
            @RequestParam Long userTypeId,
            @RequestParam("file") MultipartFile file) {
        try {
            Document document = documentService.uploadDocument(userId, userTypeId, file);
            return ResponseEntity.ok(document);
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Failed to upload document: " + e.getMessage());
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body("Error: " + e.getMessage());
        }
    }

    @PostMapping("/upload-for-test-answer")
    public ResponseEntity<?> uploadDocumentForTestAnswer(
            @RequestParam(name = "testAnswerId", required = false) Long testAnswerId,
            @RequestParam(name = "file", required = false) MultipartFile file) {

        
        try {
            // Validate parameters
            if (testAnswerId == null) {
                return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                        .body("testAnswerId is required");
            }
            
            if (file == null || file.isEmpty()) {
                return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                        .body("File is required");
            }
            
            Document document = documentService.uploadDocumentForTestAnswer(testAnswerId, file);
            return ResponseEntity.ok(document);
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Failed to upload document: " + e.getMessage());
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body("Error: " + e.getMessage());
        }
    }

    @PutMapping("/approve/{documentId}")
    public Document approveDocument(@PathVariable Long documentId) {
        return documentService.approveDocument(documentId);
    }

    @DeleteMapping("/{documentId}")
    public void deleteDocument(@PathVariable Long documentId) {
        documentService.deleteDocument(documentId);
    }
    
    @PostMapping("/test-upload")
    public ResponseEntity<String> testUpload() {
        return ResponseEntity.ok("Test endpoint working");
    }
    
    @PostMapping("/upload-for-lesson-or-analysis")
    public ResponseEntity<?> uploadDocumentForLessonOrAnalysis(
            @RequestParam Long userId,
            @RequestParam(required = false) String context,
            @RequestParam("file") MultipartFile file) {
        try {
            Document document = documentService.uploadDocumentForLessonOrAnalysis(userId, context, file);
            return ResponseEntity.ok(document);
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Failed to upload document: " + e.getMessage());
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body("Error: " + e.getMessage());
        }
    }

    @PostMapping("/upload-for-body-analysis")
    public ResponseEntity<?> uploadDocumentForBodyAnalysis(
            @RequestParam Long userId,
            @RequestParam("file") MultipartFile file,
            @RequestParam(required = false) String analysisType) {
        try {
            // Validate inputs
            if (file == null || file.isEmpty()) {
                return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                        .body("File is required");
            }
            
            // Validate user
            User user = documentService.getUserById(userId);
            if (user == null) {
                return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                        .body("Invalid user ID");
            }
            
            // Check if file is a video
            String contentType = file.getContentType();
            if (contentType == null || !contentType.startsWith("video/")) {
                return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                        .body("File must be a video for body analysis");
            }
            
            // Upload document for body analysis
            Document document = documentService.uploadDocumentForBodyAnalysis(userId, file, analysisType);
            
            // Return success response with document info
            Map<String, Object> response = new HashMap<>();
            response.put("status", "success");
            response.put("message", "Video uploaded successfully for body analysis");
            response.put("document", document);
            response.put("documentId", document.getId());
            response.put("fileName", document.getFileName());
            response.put("fileSize", document.getFileSize());
            response.put("fileType", document.getFileType());
            response.put("uploadedAt", document.getUploadedAt());
            
            return ResponseEntity.ok(response);
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Failed to upload video: " + e.getMessage());
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body("Error: " + e.getMessage());
        }
    }
    @GetMapping("/pending")
    public List<Document> getPendingDocuments() {
        return documentService.getPendingDocuments();
    }
    @GetMapping("/{documentId}/download")
    public ResponseEntity<byte[]> downloadDocument(@PathVariable Long documentId) {
        try {
            // 1. Récupérer le document en BD
            Document document = documentService.getDocumentById(documentId);
            
            if (document == null) {
                return ResponseEntity.notFound().build();
            }
            
            // 2. Charger le fichier
            File file = new File(document.getFilePath());
            
            if (!file.exists()) {
                return ResponseEntity.notFound().build();
            }
            
            // 3. Déterminer le Content-Type basé sur l'extension
            String contentType = determineContentType(document.getFileName());
            
            // 4. Lire le fichier
            byte[] fileBytes = Files.readAllBytes(file.toPath());
            
            // 5. Retourner avec les bons headers
            return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, 
                        "attachment;filename=\"" + document.getFileName() + "\"")
                .header(HttpHeaders.CONTENT_TYPE, contentType)
                .header(HttpHeaders.CONTENT_LENGTH, String.valueOf(fileBytes.length))
                .body(fileBytes);
                
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

// Méthode helper pour déterminer le type MIME
    private String determineContentType(String filename) {
        if (filename.endsWith(".mp4")) return "video/mp4";
        if (filename.endsWith(".avi")) return "video/x-msvideo";
        if (filename.endsWith(".mov")) return "video/quicktime";
        if (filename.endsWith(".mkv")) return "video/x-matroska";
        if (filename.endsWith(".pdf")) return "application/pdf";
        if (filename.endsWith(".jpg") || filename.endsWith(".jpeg")) return "image/jpeg";
        if (filename.endsWith(".png")) return "image/png";
        return "application/octet-stream";  // Default fallback
    }

    @GetMapping("/{documentId}/download-stream")
    public void downloadDocumentStream(@PathVariable Long documentId, 
                                    HttpServletResponse response) throws IOException {
        try {
            Document document = documentService.getDocumentById(documentId);
            
            if (document == null) {
                response.setStatus(HttpServletResponse.SC_NOT_FOUND);
                return;
            }
            
            File file = new File(document.getFilePath());
            
            if (!file.exists()) {
                response.setStatus(HttpServletResponse.SC_NOT_FOUND);
                return;
            }
            
            // ✅ Headers correctes
            response.setHeader(HttpHeaders.CONTENT_DISPOSITION, 
                            "attachment;filename=\"" + document.getFileName() + "\"");
            response.setHeader(HttpHeaders.CONTENT_TYPE, 
                            determineContentType(document.getFileName()));
            response.setHeader(HttpHeaders.CONTENT_LENGTH, String.valueOf(file.length()));
            
            // ✅ Stream par chunks (très efficace pour gros fichiers)
            try (FileInputStream fis = new FileInputStream(file);
                ServletOutputStream out = response.getOutputStream()) {
                
                byte[] buffer = new byte[8192];  // 8KB chunks
                int bytesRead;
                
                while ((bytesRead = fis.read(buffer)) != -1) {
                    out.write(buffer, 0, bytesRead);
                }
                out.flush();
            }
            
        } catch (IOException e) {

            response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
        }
    }

}