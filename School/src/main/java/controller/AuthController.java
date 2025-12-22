package com.auth.controller;

import com.auth.model.User;
import com.auth.model.Role;
import com.auth.service.JwtService;
import com.auth.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;
import java.util.HashMap;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@RestController
@RequestMapping("/api/auth")
@CrossOrigin(origins = {"http://localhost:4200", "https://cognitiex.com"})
public class AuthController {

    private static final Logger logger = LoggerFactory.getLogger(AuthController.class);

    @Autowired
    private AuthenticationManager authenticationManager;

    @Autowired
    private JwtService jwtService;

    @Autowired
    private UserService userService;

    /**
     * POST /api/auth/login - Authenticate user and return JWT token
     */
    @PostMapping("/login")
    public ResponseEntity<Map<String, Object>> login(@RequestBody Map<String, String> loginRequest) {
        String email = loginRequest.get("email");
        String password = loginRequest.get("password");

        try {
            logger.info("🔐 Attempting to authenticate user: {}", email);

            // Authenticate user
            Authentication authentication = authenticationManager.authenticate(
                    new UsernamePasswordAuthenticationToken(email, password)
            );

            SecurityContextHolder.getContext().setAuthentication(authentication);

            // Get user to retrieve role
            User user = userService.findByEmail(email)
                    .orElseThrow(() -> new IllegalArgumentException("User not found with email: " + email));

            // Generate JWT token
            String jwt = jwtService.generateToken(email, user.getRole().name());

            logger.info("✅ Successfully authenticated user: {}", email);

            // Log token details for debugging
            try {
                String extractedEmail = jwtService.getUsernameFromToken(jwt);
                String extractedRole = jwtService.getRoleFromToken(jwt);
                logger.info("🎫 Generated JWT token details - Email: {}, Role: {}", extractedEmail, extractedRole);
            } catch (Exception e) {
                logger.error("⚠️ Error extracting details from JWT token: {}", e.getMessage());
            }

            Map<String, Object> response = new HashMap<>();
            response.put("accessToken", jwt);
            response.put("refreshToken", jwt);
            response.put("tokenType", "Bearer");
            response.put("expiresIn", 3600); // 1 hour in seconds
            response.put("message", "Login successful");

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            logger.error("❌ Authentication failed for user: {}", email, e);
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("error", "Invalid credentials");
            errorResponse.put("message", e.getMessage());
            return ResponseEntity.status(401).body(errorResponse);
        }
    }

    /**
     * POST /api/auth/register - Register new user
     */
    @PostMapping("/register")
    public ResponseEntity<Map<String, Object>> register(@RequestBody Map<String, Object> requestData) {
        try {
            // Extract user data
            String firstname = (String) requestData.get("firstname");
            String lastname = (String) requestData.get("lastname");
            String email = (String) requestData.get("email");
            String password = (String) requestData.get("password");
            Boolean rgpdAccepted = (Boolean) requestData.get("rgpdAccepted");
            Boolean ccpaAccepted = (Boolean) requestData.get("ccpaAccepted");
            Boolean commercialUseConsent = (Boolean) requestData.get("commercialUseConsent");

            logger.info("📝 Attempting to register user: {}", email);

            // Validate required fields
            if (firstname == null || lastname == null || email == null || password == null) {
                Map<String, Object> errorResponse = new HashMap<>();
                errorResponse.put("error", "All fields are required");
                return ResponseEntity.status(400).body(errorResponse);
            }

            // Validate required consents
            if (rgpdAccepted == null || !rgpdAccepted) {
                Map<String, Object> errorResponse = new HashMap<>();
                errorResponse.put("error", "RGPD consent is required");
                return ResponseEntity.status(400).body(errorResponse);
            }

            if (commercialUseConsent == null || !commercialUseConsent) {
                Map<String, Object> errorResponse = new HashMap<>();
                errorResponse.put("error", "Commercial use consent is required");
                return ResponseEntity.status(400).body(errorResponse);
            }

            // Check if user already exists
            if (userService.findByEmail(email).isPresent()) {
                Map<String, Object> errorResponse = new HashMap<>();
                errorResponse.put("error", "Email already registered");
                return ResponseEntity.status(400).body(errorResponse);
            }

            // Create new user
            User newUser = new User();
            newUser.setFirstname(firstname);
            newUser.setLastname(lastname);
            newUser.setEmail(email);
            newUser.setPassword(password);
            newUser.setRole(Role.USER);
            newUser.setEnabled(true);  // ← AJOUTER CETTE LIGNE


            // Set privacy consents
            if (rgpdAccepted != null && rgpdAccepted) {
                newUser.setRgpdAccepted(true);
                newUser.setRgpdAcceptedAt(java.time.LocalDateTime.now());
            }

            if (ccpaAccepted != null && ccpaAccepted) {
                newUser.setCcpaAccepted(true);
                newUser.setCcpaAcceptedAt(java.time.LocalDateTime.now());
            }

            if (commercialUseConsent != null && commercialUseConsent) {
                newUser.setCommercialUseConsent(true);
                newUser.setCommercialUseConsentAt(java.time.LocalDateTime.now());
            }

            // Save user
            userService.createUser(newUser);

            // Get user to retrieve role
            User user = userService.findByEmail(email)
                    .orElseThrow(() -> new IllegalArgumentException("User not found with email: " + email));

            // Generate JWT token
            String jwt = jwtService.generateToken(email, user.getRole().name());

            try {
                String extractedEmail = jwtService.getUsernameFromToken(jwt);
                String extractedRole = jwtService.getRoleFromToken(jwt);
                logger.info("🎫 Generated JWT token details - Email: {}, Role: {}", extractedEmail, extractedRole);
            } catch (Exception e) {
                logger.error("⚠️ Error extracting details from JWT token: {}", e.getMessage());
            }

            logger.info("✅ User registered successfully: {}", email);

            Map<String, Object> response = new HashMap<>();
            response.put("accessToken", jwt);
            response.put("refreshToken", jwt);
            response.put("tokenType", "Bearer");
            response.put("expiresIn", 3600); // 1 hour in seconds
            response.put("message", "Registration successful");

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            logger.error("❌ Registration failed: {}", e.getMessage(), e);
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("error", "Registration failed");
            errorResponse.put("message", e.getMessage());
            return ResponseEntity.status(500).body(errorResponse);
        }
    }

    /**
     * POST /api/auth/refresh-token - Refresh JWT token
     */
    @PostMapping("/refresh-token")
    public ResponseEntity<Map<String, Object>> refreshToken(@RequestBody Map<String, String> refreshRequest) {
        String refreshToken = refreshRequest.get("refreshToken");

        try {
            logger.info("🔄 Attempting to refresh token");

            // Validate refresh token
            if (refreshToken == null || refreshToken.isEmpty()) {
                Map<String, Object> errorResponse = new HashMap<>();
                errorResponse.put("error", "Refresh token is required");
                return ResponseEntity.status(400).body(errorResponse);
            }

            // Extract username from refresh token
            String username = jwtService.getUsernameFromToken(refreshToken);
            if (username == null || username.isEmpty()) {
                Map<String, Object> errorResponse = new HashMap<>();
                errorResponse.put("error", "Invalid refresh token");
                return ResponseEntity.status(401).body(errorResponse);
            }

            // Get user to retrieve role
            User user = userService.findByEmail(username)
                    .orElseThrow(() -> new IllegalArgumentException("User not found with email: " + username));

            // Validate refresh token
            if (!jwtService.validateToken(refreshToken, username)) {
                Map<String, Object> errorResponse = new HashMap<>();
                errorResponse.put("error", "Invalid or expired refresh token");
                return ResponseEntity.status(401).body(errorResponse);
            }

            // Generate new JWT token
            String newJwt = jwtService.generateToken(username, user.getRole().name());

            logger.info("✅ Successfully refreshed token for user: {}", username);

            Map<String, Object> response = new HashMap<>();
            response.put("accessToken", newJwt);
            response.put("refreshToken", newJwt);
            response.put("tokenType", "Bearer");
            response.put("expiresIn", 3600); // 1 hour in seconds
            response.put("message", "Token refreshed successfully");

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            logger.error("❌ Token refresh failed: {}", e.getMessage(), e);
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("error", "Token refresh failed");
            errorResponse.put("message", e.getMessage());
            return ResponseEntity.status(401).body(errorResponse);
        }
    }

    /**
     * ⚠️ NOTE: DO NOT USE THIS ENDPOINT
     * Use /api/user/profile instead (UserController)
     * This endpoint is kept for backward compatibility but should be removed
     */
    @Deprecated
    @GetMapping("/profile")
    public ResponseEntity<Map<String, Object>> getProfile() {
        logger.warn("⚠️ DEPRECATED: /api/auth/profile endpoint called. Use /api/user/profile instead");
        Map<String, Object> errorResponse = new HashMap<>();
        errorResponse.put("error", "Deprecated endpoint. Use /api/user/profile instead");
        return ResponseEntity.status(410).body(errorResponse); // 410 Gone
    }
}