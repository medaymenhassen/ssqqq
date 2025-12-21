package com.auth.controller;

import com.auth.model.User;
import com.auth.service.JwtService;
import com.auth.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;
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

    @Autowired
    private PasswordEncoder passwordEncoder;

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody Map<String, String> loginRequest) {
        String email = loginRequest.get("email");
        String password = loginRequest.get("password");
        
        try {
            logger.info("Attempting to authenticate user: {}", email);
            logger.info("Password provided: {}", password);

            Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(email, password)
            );

            SecurityContextHolder.getContext().setAuthentication(authentication);
            // Get user to retrieve role
            User user = userService.findByEmail(email)
                .orElseThrow(() -> new IllegalArgumentException("User not found with email: " + email));
            String jwt = jwtService.generateToken(email, user.getRole().name());

            logger.info("Successfully authenticated user: {}", email);

            Map<String, Object> response = new HashMap<>();
            response.put("accessToken", jwt);
            response.put("tokenType", "Bearer");
            response.put("expiresIn", 3600); // 1 hour
            response.put("message", "Login successful");
            // For simplicity, we're using the same token as refresh token
            // In a production environment, you'd want a separate refresh token
            response.put("refreshToken", jwt);
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            logger.error("Authentication failed for user: {}", email, e);
            Map<String, String> errorResponse = new HashMap<>();
            errorResponse.put("error", "Invalid credentials");
            return ResponseEntity.status(401).body(errorResponse);
        }
    }

    @PostMapping("/register")
    public ResponseEntity<?> register(@RequestBody Map<String, Object> requestData) {
        try {
            // Extract user data
            String firstname = (String) requestData.get("firstname");
            String lastname = (String) requestData.get("lastname");
            String email = (String) requestData.get("email");
            String password = (String) requestData.get("password");
            Boolean rgpdAccepted = (Boolean) requestData.get("rgpdAccepted");
            Boolean ccpaAccepted = (Boolean) requestData.get("ccpaAccepted");
            
            // Validate required fields
            if (firstname == null || lastname == null || email == null || password == null) {
                Map<String, String> errorResponse = new HashMap<>();
                errorResponse.put("error", "All fields are required");
                return ResponseEntity.status(400).body(errorResponse);
            }
            
            // Check if user already exists
            if (userService.findByEmail(email).isPresent()) {
                Map<String, String> errorResponse = new HashMap<>();
                errorResponse.put("error", "Email already registered");
                return ResponseEntity.status(400).body(errorResponse);
            }

            // Create new user
            User newUser = new User();
            newUser.setFirstname(firstname);
            newUser.setLastname(lastname);
            newUser.setEmail(email);
            newUser.setPassword(password);
            // Set default role
            newUser.setRole(com.auth.model.Role.USER);            
            // Set privacy consent
            if (rgpdAccepted != null && rgpdAccepted) {
                newUser.setRgpdAccepted(true);
                newUser.setRgpdAcceptedAt(java.time.LocalDateTime.now());
            }
            
            if (ccpaAccepted != null && ccpaAccepted) {
                newUser.setCcpaAccepted(true);
                newUser.setCcpaAcceptedAt(java.time.LocalDateTime.now());
            }
            
            userService.createUser(newUser);

            // Get user to retrieve role
            User user = userService.findByEmail(email)
                .orElseThrow(() -> new IllegalArgumentException("User not found with email: " + email));
            // Generate token for new user
            String jwt = jwtService.generateToken(email, user.getRole().name());

            Map<String, Object> response = new HashMap<>();
            response.put("accessToken", jwt);
            response.put("tokenType", "Bearer");
            response.put("expiresIn", 3600); // 1 hour
            response.put("message", "Registration successful");
            // For simplicity, we're using the same token as refresh token
            // In a production environment, you'd want a separate refresh token
            response.put("refreshToken", jwt);
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, String> errorResponse = new HashMap<>();
            errorResponse.put("error", "Registration failed: " + e.getMessage());
            return ResponseEntity.status(500).body(errorResponse);
        }
    }
}