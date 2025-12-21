package com.auth.controller;

import com.auth.model.Document;
import com.auth.model.User;
import com.auth.model.UserType;
import com.auth.service.DocumentService;
import com.auth.service.UserService;
import com.auth.service.UserTypeService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.HashMap;

@RestController
@RequestMapping("/api/special-user-requests")
@CrossOrigin(origins = {"http://localhost:4200", "https://cognitiex.com"})
public class SpecialUserRequestController {

    @Autowired
    private DocumentService documentService;

    @Autowired
    private UserService userService;

    @Autowired
    private UserTypeService userTypeService;

    /**
     * Submit a request to become a special user by uploading documents
     */
    @PostMapping("/submit-request")
    public ResponseEntity<?> submitSpecialUserRequest(
            @RequestParam Long userId,
            @RequestParam Long userTypeId,
            @RequestParam("documents") List<MultipartFile> files) {
        try {
            // Validate user and user type
            User user = userService.getUserById(userId)
                    .orElseThrow(() -> new RuntimeException("User not found"));
            
            UserType userType = userTypeService.getUserTypeById(userTypeId)
                    .orElseThrow(() -> new RuntimeException("User type not found"));
            
            // Upload documents
            for (MultipartFile file : files) {
                documentService.uploadDocument(userId, userTypeId, file);
            }
            
            Map<String, Object> response = new HashMap<>();
            response.put("message", "Special user request submitted successfully. Your documents are under review.");
            response.put("userId", userId);
            response.put("userTypeId", userTypeId);
            response.put("documentCount", files.size());
            
            return ResponseEntity.ok(response);
        } catch (IOException e) {
            Map<String, String> errorResponse = new HashMap<>();
            errorResponse.put("error", "Failed to upload documents: " + e.getMessage());
            return ResponseEntity.status(500).body(errorResponse);
        } catch (Exception e) {
            Map<String, String> errorResponse = new HashMap<>();
            errorResponse.put("error", "Request failed: " + e.getMessage());
            return ResponseEntity.status(400).body(errorResponse);
        }
    }

    /**
     * Get all pending special user requests (for admins)
     */
    @GetMapping("/pending")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<?> getPendingRequests() {
        try {
            List<Document> pendingDocuments = documentService.getPendingDocuments();
            return ResponseEntity.ok(pendingDocuments);
        } catch (Exception e) {
            Map<String, String> errorResponse = new HashMap<>();
            errorResponse.put("error", "Failed to retrieve pending requests: " + e.getMessage());
            return ResponseEntity.status(500).body(errorResponse);
        }
    }

    /**
     * Approve a special user request
     */
    @PostMapping("/approve/{documentId}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<?> approveSpecialUserRequest(@PathVariable Long documentId) {
        try {
            // Approve the document
            Document document = documentService.approveDocument(documentId);
            
            // Update user's user type if all required documents are approved
            User user = document.getUser();
            UserType userType = document.getUserType();
            
            // For simplicity, we'll update the user type immediately
            // In a real application, you might want to check if all required documents are approved
            user.setUserType(userType);
            userService.updateUser(user.getId(), user);
            
            Map<String, Object> response = new HashMap<>();
            response.put("message", "Special user request approved successfully");
            response.put("documentId", documentId);
            response.put("userId", user.getId());
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, String> errorResponse = new HashMap<>();
            errorResponse.put("error", "Failed to approve request: " + e.getMessage());
            return ResponseEntity.status(500).body(errorResponse);
        }
    }

    /**
     * Reject a special user request
     */
    @DeleteMapping("/reject/{documentId}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<?> rejectSpecialUserRequest(@PathVariable Long documentId) {
        try {
            // Delete the document (reject the request)
            documentService.deleteDocument(documentId);
            
            Map<String, Object> response = new HashMap<>();
            response.put("message", "Special user request rejected successfully");
            response.put("documentId", documentId);
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, String> errorResponse = new HashMap<>();
            errorResponse.put("error", "Failed to reject request: " + e.getMessage());
            return ResponseEntity.status(500).body(errorResponse);
        }
    }

    /**
     * Get documents for a specific user's special user request
     */
    @GetMapping("/user/{userId}")
    public ResponseEntity<?> getUserDocuments(@PathVariable Long userId) {
        try {
            List<Document> documents = documentService.getDocumentsByUser(userId);
            return ResponseEntity.ok(documents);
        } catch (Exception e) {
            Map<String, String> errorResponse = new HashMap<>();
            errorResponse.put("error", "Failed to retrieve documents: " + e.getMessage());
            return ResponseEntity.status(500).body(errorResponse);
        }
    }
}