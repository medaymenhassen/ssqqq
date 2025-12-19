package com.auth.controller;

import com.auth.dto.LoginRequest;
import com.auth.dto.LoginResponse;
import com.auth.dto.LogoutRequest;
import com.auth.dto.RegisterRequest;
import com.auth.model.User;
import com.auth.service.AuthService;
import jakarta.validation.Valid;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private static final Logger logger = LoggerFactory.getLogger(AuthController.class);

    private final AuthService authService;

    public AuthController(AuthService authService) {
        this.authService = authService;
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@Valid @RequestBody LoginRequest request) {
        try {
            LoginResponse response = authService.login(request);
            logger.info("Utilisateur connecté: {}", request.getEmail());
            
            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(createErrorResponse(e.getMessage(), 401));
        } catch (Exception e) {
            logger.error("Erreur lors de la connexion: {}", e.getMessage());
            return ResponseEntity.internalServerError()
                    .body(createErrorResponse("Erreur lors de la connexion", 500));
        }
    }

    @PostMapping("/register")
    public ResponseEntity<?> register(@Valid @RequestBody RegisterRequest request) {
        try {
            // Check if passwords match
            if (!request.isPasswordsMatching()) {
                return ResponseEntity.badRequest()
                        .body(createErrorResponse("Les mots de passe ne correspondent pas", 400));
            }

            LoginResponse response = authService.register(request);
            logger.info("Nouvel utilisateur enregistré: {}", request.getEmail());
            
            return ResponseEntity.status(HttpStatus.CREATED).body(response);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest()
                    .body(createErrorResponse(e.getMessage(), 400));
        } catch (Exception e) {
            logger.error("Erreur lors de l'enregistrement: {}", e.getMessage());
            return ResponseEntity.internalServerError()
                    .body(createErrorResponse("Erreur lors de l'enregistrement", 500));
        }
    }

    @PostMapping("/logout")
    public ResponseEntity<?> logout(@RequestBody LogoutRequest request) {
        try {
            // Get authenticated user
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            
            if (authentication == null || !authentication.isAuthenticated()) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                        .body(createErrorResponse("Utilisateur non authentifié", 401));
            }

            User user = (User) authentication.getPrincipal();

            // Logout user
            authService.logout(request.getAccessToken(), request.getRefreshToken(), user);
            
            // Clear security context
            SecurityContextHolder.clearContext();
            
            logger.info("Utilisateur déconnecté: {}", user.getEmail());
            
            Map<String, Object> response = new HashMap<>();
            response.put("message", "Déconnexion réussie");
            response.put("success", true);
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            logger.error("Erreur lors de la déconnexion: {}", e.getMessage());
            return ResponseEntity.internalServerError()
                    .body(createErrorResponse("Erreur lors de la déconnexion", 500));
        }
    }

    private Map<String, Object> createErrorResponse(String message, int code) {
        Map<String, Object> errorResponse = new HashMap<>();
        errorResponse.put("message", message);
        errorResponse.put("code", code);
        errorResponse.put("timestamp", System.currentTimeMillis());
        return errorResponse;
    }
}