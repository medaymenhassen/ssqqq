package com.auth.controller;

import com.auth.model.Document;
import com.auth.service.DocumentService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;

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
        System.out.println("=== Document Upload Endpoint Hit ===");
        System.out.println("Received document upload request for testAnswerId: " + testAnswerId + ", file: " + (file != null ? file.getOriginalFilename() : "null"));
        System.out.println("File size: " + (file != null ? file.getSize() : "null"));
        System.out.println("Content type: " + (file != null ? file.getContentType() : "null"));
        
        try {
            // Validate parameters
            if (testAnswerId == null) {
                System.out.println("testAnswerId is null");
                return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                        .body("testAnswerId is required");
            }
            
            if (file == null || file.isEmpty()) {
                System.out.println("File is null or empty");
                return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                        .body("File is required");
            }
            
            Document document = documentService.uploadDocumentForTestAnswer(testAnswerId, file);
            System.out.println("Document uploaded successfully: " + document.getFileName());
            return ResponseEntity.ok(document);
        } catch (IOException e) {
            System.out.println("IO Exception during document upload: " + e.getMessage());
            e.printStackTrace();
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Failed to upload document: " + e.getMessage());
        } catch (Exception e) {
            System.out.println("Exception during document upload: " + e.getMessage());
            e.printStackTrace();
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

    @GetMapping("/pending")
    public List<Document> getPendingDocuments() {
        return documentService.getPendingDocuments();
    }
}