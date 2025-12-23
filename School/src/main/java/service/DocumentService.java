package com.auth.service;

import com.auth.model.Document;
import com.auth.model.User;
import com.auth.model.UserType;
import com.auth.model.TestAnswer;
import com.auth.repository.DocumentRepository;
import com.auth.repository.UserRepository;
import com.auth.repository.UserTypeRepository;
import com.auth.repository.TestAnswerRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import jakarta.annotation.PostConstruct;

import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import com.auth.model.User;
import com.auth.repository.UserRepository;

@Service
public class DocumentService {

    @Autowired
    private DocumentRepository documentRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private UserTypeRepository userTypeRepository;
    
    @Autowired
    private TestAnswerRepository testAnswerRepository;

    // Directory where uploaded files will be stored in resources
    private final String uploadDir = System.getProperty("user.dir") + "/src/main/resources/static/uploads/";
    
    @PostConstruct
    public void init() {
        try {
            Path uploadPath = Paths.get(uploadDir);
            if (!Files.exists(uploadPath)) {
                Files.createDirectories(uploadPath);

            }
        } catch (IOException e) {
            System.err.println("Failed to create upload directory: " + e.getMessage());
        }
    }

    public List<Document> getAllDocuments() {
        return documentRepository.findAll();
    }

    public List<Document> getDocumentsByUser(Long userId) {
        return documentRepository.findByUserId(userId);
    }

    public List<Document> getDocumentsByUserType(Long userTypeId) {
        return documentRepository.findByUserTypeId(userTypeId);
    }

    public Document uploadDocument(Long userId, Long userTypeId, MultipartFile file) throws IOException {
        // Get user and user type
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found"));
        
        UserType userType = userTypeRepository.findById(userTypeId)
                .orElseThrow(() -> new RuntimeException("User type not found"));

        // Create upload directory if it doesn't exist
        Path uploadPath = Paths.get(uploadDir);
        if (!Files.exists(uploadPath)) {
            Files.createDirectories(uploadPath);
        }

        // Generate unique filename
        String originalFilename = file.getOriginalFilename();
        String fileExtension = "";
        if (originalFilename != null && originalFilename.contains(".")) {
            fileExtension = originalFilename.substring(originalFilename.lastIndexOf("."));
        }
        String uniqueFilename = UUID.randomUUID().toString() + fileExtension;

        // Save file to disk
        Path filePath = uploadPath.resolve(uniqueFilename);
        Files.copy(file.getInputStream(), filePath, StandardCopyOption.REPLACE_EXISTING);

        // Create document record
        Document document = new Document();
        document.setFileName(originalFilename);
        document.setFileType(getFileType(file.getContentType(), file));
        document.setFilePath(filePath.toString());
        document.setFileSize(file.getSize());
        document.setUser(user);
        document.setUserType(userType);
        document.setUploadedAt(LocalDateTime.now());
        document.setApproved(false); // Default to not approved

        return documentRepository.save(document);
    }

    public Document uploadDocumentForTestAnswer(Long testAnswerId, MultipartFile file) throws IOException {
        // Get test answer
        TestAnswer testAnswer = testAnswerRepository.findById(testAnswerId)
                .orElseThrow(() -> new RuntimeException("Test answer not found"));

        // Create upload directory if it doesn't exist
        Path uploadPath = Paths.get(uploadDir);
        if (!Files.exists(uploadPath)) {
            Files.createDirectories(uploadPath);
        }

        // Generate unique filename
        String originalFilename = file.getOriginalFilename();
        String fileExtension = "";
        if (originalFilename != null && originalFilename.contains(".")) {
            fileExtension = originalFilename.substring(originalFilename.lastIndexOf("."));
        }
        String uniqueFilename = UUID.randomUUID().toString() + fileExtension;

        // Save file to disk
        Path filePath = uploadPath.resolve(uniqueFilename);
        Files.copy(file.getInputStream(), filePath, StandardCopyOption.REPLACE_EXISTING);

        // Get current authenticated user
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        User currentUser = null;
        if (authentication != null) {
            
            if (authentication.getPrincipal() instanceof org.springframework.security.core.userdetails.User) {
                String username = ((org.springframework.security.core.userdetails.User) authentication.getPrincipal()).getUsername();
                Optional<User> userOpt = userRepository.findByEmail(username);
                if (userOpt.isPresent()) {
                    currentUser = userOpt.get();
                } else {
                    // User not found for email
                }
            } else if (authentication.getPrincipal() instanceof String) {
                // Sometimes the principal is just the username/email as a string
                String username = (String) authentication.getPrincipal();
                Optional<User> userOpt = userRepository.findByEmail(username);
                if (userOpt.isPresent()) {
                    currentUser = userOpt.get();
                } else {
                    // User not found for email
                }
            } else {
                // Unknown principal type
            }
        } else {
            // No authentication found
        }
        
        // Create document record
        Document document = new Document();
        document.setFileName(originalFilename);
        document.setFileType(getFileType(file.getContentType(), file));
        document.setFilePath(filePath.toString());
        document.setFileSize(file.getSize());
        document.setTestAnswer(testAnswer);
        // Set the current user if available
        if (currentUser != null) {
            document.setUser(currentUser);
        } else {
            // Fallback: try to get any user
            List<User> allUsers = userRepository.findAll();
            if (!allUsers.isEmpty()) {
                User fallbackUser = allUsers.get(0); // Use the first user
                document.setUser(fallbackUser);
            } else {
                // This should never happen in a real application
                throw new RuntimeException("No users available to associate with document");
            }
        }
        document.setUploadedAt(LocalDateTime.now());
        document.setApproved(false); // Default to not approved

        return documentRepository.save(document);
    }

    public Document approveDocument(Long documentId) {
        Document document = documentRepository.findById(documentId)
                .orElseThrow(() -> new RuntimeException("Document not found"));
        
        document.setApproved(true);
        return documentRepository.save(document);
    }

    public void deleteDocument(Long documentId) {
        Document document = documentRepository.findById(documentId)
                .orElseThrow(() -> new RuntimeException("Document not found"));
        
        // Delete file from disk
        try {
            Path filePath = Paths.get(document.getFilePath());
            Files.deleteIfExists(filePath);
        } catch (IOException e) {
            // Continue with database deletion
        }
        
        documentRepository.deleteById(documentId);
    }

    public List<Document> getPendingDocuments() {
        return documentRepository.findByApproved(false);
    }

    public Document uploadDocumentForLessonOrAnalysis(Long userId, String context, MultipartFile file) throws IOException {
        // Get user
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found"));

        // Create upload directory if it doesn't exist
        Path uploadPath = Paths.get(uploadDir);
        if (!Files.exists(uploadPath)) {
            Files.createDirectories(uploadPath);
        }

        // Generate unique filename
        String originalFilename = file.getOriginalFilename();
        String fileExtension = "";
        if (originalFilename != null && originalFilename.contains(".")) {
            fileExtension = originalFilename.substring(originalFilename.lastIndexOf("."));
        }
        String uniqueFilename = UUID.randomUUID().toString() + fileExtension;

        // Save file to disk
        Path filePath = uploadPath.resolve(uniqueFilename);
        Files.copy(file.getInputStream(), filePath, StandardCopyOption.REPLACE_EXISTING);

        // Create document record
        Document document = new Document();
        document.setFileName(originalFilename);
        document.setFileType(getFileType(file.getContentType(), file));
        document.setFilePath(filePath.toString());
        document.setFileSize(file.getSize());
        document.setUser(user);
        document.setUploadedAt(LocalDateTime.now());
        document.setApproved(false); // Default to not approved
        
        // Add context information to the filename or as metadata
        if (context != null && !context.isEmpty()) {
            document.setFileName(context + "_" + originalFilename);
        }

        return documentRepository.save(document);
    }

    private String getFileType(String contentType, MultipartFile file) {
        if (contentType == null) {
            return "UNKNOWN";
        }
        
        if (contentType.startsWith("image/")) {
            return "IMAGE";
        } else if (contentType.equals("application/pdf")) {
            return "PDF";
        } else if (contentType.startsWith("video/")) {
            // Specifically handle MP4 videos
            if (contentType.equals("video/mp4")) {
                return "MP4_VIDEO";
            }
            return "VIDEO";
        } else if (contentType.equals("model/gltf-binary") || 
                   contentType.equals("model/gltf+json") || 
                   (contentType.equals("application/octet-stream") && 
                    file != null && 
                    file.getOriginalFilename() != null && 
                    file.getOriginalFilename().toLowerCase().endsWith(".glb"))) {
            // Handle GLB 3D models
            return "GLB_3D_MODEL";
        } else {
            return "OTHER";
        }
    }
    
    public Document uploadDocumentForBodyAnalysis(Long userId, MultipartFile file, String analysisType) throws IOException {
        // Get user
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found"));

        // Create upload directory if it doesn't exist
        Path uploadPath = Paths.get(uploadDir);
        if (!Files.exists(uploadPath)) {
            Files.createDirectories(uploadPath);
        }

        // Generate unique filename
        String originalFilename = file.getOriginalFilename();
        String fileExtension = "";
        if (originalFilename != null && originalFilename.contains(".")) {
            fileExtension = originalFilename.substring(originalFilename.lastIndexOf("."));
        }
        String uniqueFilename = UUID.randomUUID().toString() + fileExtension;

        // Save file to disk
        Path filePath = uploadPath.resolve(uniqueFilename);
        Files.copy(file.getInputStream(), filePath, StandardCopyOption.REPLACE_EXISTING);

        // Create document record
        Document document = new Document();
        document.setFileName(originalFilename);
        document.setFileType(getFileType(file.getContentType(), file));
        document.setFilePath(filePath.toString());
        document.setFileSize(file.getSize());
        document.setUser(user);
        document.setUploadedAt(LocalDateTime.now());
        document.setApproved(false); // Default to not approved
        
        // Add analysis type information to the filename or as metadata
        if (analysisType != null && !analysisType.isEmpty()) {
            document.setFileName("body_analysis_" + analysisType + "_" + originalFilename);
        } else {
            document.setFileName("body_analysis_" + originalFilename);
        }

        return documentRepository.save(document);
    }
    
    public User getUserById(Long userId) {
        return userRepository.findById(userId).orElse(null);
    }
    
    public Document getDocumentById(Long documentId) {
        return documentRepository.findById(documentId).orElse(null);
    }
}