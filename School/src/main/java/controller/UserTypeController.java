package com.auth.controller;

import com.auth.dto.UserTypeRequest;
import com.auth.dto.UserTypeResponse;
import com.auth.dto.DocumentResponse;
import com.auth.service.UserTypeService;
import jakarta.validation.Valid;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/user-types")
public class UserTypeController {

    private static final Logger log = LoggerFactory.getLogger(UserTypeController.class);

    private final UserTypeService userTypeService;

    public UserTypeController(UserTypeService userTypeService) {
        this.userTypeService = userTypeService;
    }

    /**
     * Créer un nouveau type d'utilisateur
     * POST /api/user-types
     */
    @PostMapping
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<?> createUserType(@Valid @RequestBody UserTypeRequest request) {
        try {
            UserTypeResponse response = userTypeService.createUserType(request);
            log.info("Type créé: {}", response.getNom());
            
            return ResponseEntity.status(HttpStatus.CREATED).body(response);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest()
                    .body(createErrorResponse(e.getMessage(), 400));
        } catch (Exception e) {
            log.error("Erreur lors de la création: {}", e.getMessage());
            return ResponseEntity.internalServerError()
                    .body(createErrorResponse("Erreur lors de la création", 500));
        }
    }

    /**
     * Récupérer tous les types d'utilisateurs
     * GET /api/user-types
     */
    @GetMapping
    public ResponseEntity<?> getAllUserTypes() {
        try {
            List<UserTypeResponse> types = userTypeService.getAllUserTypes();
            log.info("Récupération de {} types", types.size());
            
            return ResponseEntity.ok(types);
        } catch (Exception e) {
            log.error("Erreur: {}", e.getMessage());
            return ResponseEntity.internalServerError()
                    .body(createErrorResponse("Erreur lors de la récupération", 500));
        }
    }

    /**
     * Récupérer les types spéciaux uniquement
     * GET /api/user-types/special
     */
    @GetMapping("/special")
    public ResponseEntity<?> getSpecialUserTypes() {
        try {
            List<UserTypeResponse> types = userTypeService.getSpecialUserTypes();
            log.info("Récupération de {} types spéciaux", types.size());
            
            return ResponseEntity.ok(types);
        } catch (Exception e) {
            log.error("Erreur: {}", e.getMessage());
            return ResponseEntity.internalServerError()
                    .body(createErrorResponse("Erreur lors de la récupération", 500));
        }
    }

    /**
     * Récupérer les types normaux uniquement
     * GET /api/user-types/normal
     */
    @GetMapping("/normal")
    public ResponseEntity<?> getNormalUserTypes() {
        try {
            List<UserTypeResponse> types = userTypeService.getNormalUserTypes();
            log.info("Récupération de {} types normaux", types.size());
            
            return ResponseEntity.ok(types);
        } catch (Exception e) {
            log.error("Erreur: {}", e.getMessage());
            return ResponseEntity.internalServerError()
                    .body(createErrorResponse("Erreur lors de la récupération", 500));
        }
    }

    /**
     * Récupérer un type par ID
     * GET /api/user-types/{id}
     */
    @GetMapping("/{id}")
    public ResponseEntity<?> getUserTypeById(@PathVariable Long id) {
        try {
            UserTypeResponse response = userTypeService.getUserTypeById(id);
            
            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(createErrorResponse(e.getMessage(), 404));
        } catch (Exception e) {
            log.error("Erreur: {}", e.getMessage());
            return ResponseEntity.internalServerError()
                    .body(createErrorResponse("Erreur lors de la récupération", 500));
        }
    }

    /**
     * Récupérer les documents d'un type
     * GET /api/user-types/{id}/documents
     * 
     * ⚠️ Si isSpecial = false → liste vide
     * ✅ Si isSpecial = true → documents retournés
     */
    @GetMapping("/{id}/documents")
    public ResponseEntity<?> getDocuments(@PathVariable Long id) {
        try {
            List<DocumentResponse> documents = userTypeService.getDocumentsByUserType(id);
            
            Map<String, Object> response = new HashMap<>();
            response.put("userTypeId", id);
            response.put("documentsCount", documents.size());
            response.put("documents", documents);
            
            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(createErrorResponse(e.getMessage(), 404));
        } catch (Exception e) {
            log.error("Erreur: {}", e.getMessage());
            return ResponseEntity.internalServerError()
                    .body(createErrorResponse("Erreur lors de la récupération", 500));
        }
    }

    /**
     * Mettre à jour un type
     * PUT /api/user-types/{id}
     */
    @PutMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<?> updateUserType(
            @PathVariable Long id,
            @Valid @RequestBody UserTypeRequest request) {
        try {
            UserTypeResponse response = userTypeService.updateUserType(id, request);
            log.info("Type mis à jour: {}", response.getNom());
            
            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(createErrorResponse(e.getMessage(), 404));
        } catch (Exception e) {
            log.error("Erreur: {}", e.getMessage());
            return ResponseEntity.internalServerError()
                    .body(createErrorResponse("Erreur lors de la mise à jour", 500));
        }
    }

    /**
     * Supprimer un type
     * DELETE /api/user-types/{id}
     */
    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<?> deleteUserType(@PathVariable Long id) {
        try {
            userTypeService.deleteUserType(id);
            log.info("Type supprimé: {}", id);
            
            Map<String, Object> response = new HashMap<>();
            response.put("message", "Type supprimé avec succès");
            response.put("success", true);
            
            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(createErrorResponse(e.getMessage(), 404));
        } catch (Exception e) {
            log.error("Erreur: {}", e.getMessage());
            return ResponseEntity.internalServerError()
                    .body(createErrorResponse("Erreur lors de la suppression", 500));
        }
    }

    /**
     * Créer une réponse d'erreur standardisée
     */
    private Map<String, Object> createErrorResponse(String message, int status) {
        Map<String, Object> error = new HashMap<>();
        error.put("error", message);
        error.put("status", status);
        error.put("success", false);
        return error;
    }
}