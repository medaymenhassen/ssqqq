package com.auth.controller;

import com.auth.model.User;
import com.auth.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = {"http://localhost:4200", "https://cognitiex.com"})
public class UserController {

    private static final Logger logger = LoggerFactory.getLogger(UserController.class);

    @Autowired
    private UserService userService;

    @GetMapping("/user/profile")
    public ResponseEntity<?> getCurrentUserProfile() {
        try {
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            
            logger.info("🔍 Profile endpoint - Authentication details: Principal={}, Authenticated={}, Authorities={}", 
                authentication != null ? authentication.getPrincipal() : null,
                authentication != null ? authentication.isAuthenticated() : false,
                authentication != null ? authentication.getAuthorities() : null);
            
            if (authentication == null || !authentication.isAuthenticated()) {
                logger.warn("❌ Profile endpoint - No authentication or not authenticated");
                return ResponseEntity.status(401).build();  // ✅ .build() au lieu de .body(null)
            }  // ✅ Fermeture correcte du if
            
            String email;
            Object principal = authentication.getPrincipal();
            if (principal instanceof String) {
                email = (String) principal;
            } else if (principal instanceof org.springframework.security.core.userdetails.UserDetails) {
                email = ((org.springframework.security.core.userdetails.UserDetails) principal).getUsername();
            } else {
                email = authentication.getName();
            }
            
            if ("anonymousUser".equals(email)) {
                logger.warn("❌ Profile endpoint - Anonymous user access attempt");
                return ResponseEntity.status(401).build();  // ✅ Au lieu de 500
            }
            
            Optional<User> userOptional = userService.findByEmail(email);
            if (!userOptional.isPresent()) {
                logger.warn("❌ Profile endpoint - User not found with email: {}", email);
                return ResponseEntity.notFound().build();
            }
            
            logger.info("✅ Profile endpoint - User found, returning profile for: {}", email);
            User user = userOptional.get();
            user.setPassword(null);
            return ResponseEntity.ok(user);
            
        } catch (Exception e) {
            logger.error("❌ Error in profile endpoint: {}", e.getMessage(), e);
            return ResponseEntity.status(500).build();
        }
    }

    /**
     * GET /api/user/profile/{id} - Get user profile by ID
     * This endpoint retrieves the profile of a user by their ID
     */
    @GetMapping("/user/profile/{id}")
    public ResponseEntity<User> getUserProfileById(@PathVariable Long id) {
        try {
            Optional<User> userOptional = userService.getUserById(id);
            if (!userOptional.isPresent()) {
                return ResponseEntity.notFound().build();
            }
            
            User user = userOptional.get();
            // 🔒 SECURITY: Never return password
            user.setPassword(null);
            return ResponseEntity.ok(user);
            
        } catch (Exception e) {
            return ResponseEntity.status(500).body(null);
        }
    }

    /**
     * GET /api/users - Get all users (ADMIN only)
     */
    @GetMapping("/users")
    public List<User> getAllUsers() {
        logger.info("📋 Fetching all users");
        return userService.getAllUsers();
    }

    /**
     * GET /api/users/{id} - Get user by ID
     */
    @GetMapping("/users/{id}")
    public ResponseEntity<User> getUserById(@PathVariable Long id) {
        logger.info("📋 Fetching user by ID: {}", id);
        Optional<User> user = userService.getUserById(id);
        if (!user.isPresent()) {
            logger.warn("❌ User not found with ID: {}", id);
            return ResponseEntity.notFound().build();
        }
        
        // 🔒 SECURITY: Never return password
        User userEntity = user.get();
        userEntity.setPassword(null);
        return ResponseEntity.ok(userEntity);
    }

    /**
     * POST /api/users - Create new user (ADMIN only)
     */
    @PostMapping("/users")
    public ResponseEntity<User> createUser(@RequestBody User user) {
        try {
            logger.info("➕ Creating new user: {}", user.getEmail());
            User createdUser = userService.createUser(user);
            createdUser.setPassword(null);
            return ResponseEntity.ok(createdUser);
        } catch (Exception e) {
            logger.error("❌ Error creating user: {}", e.getMessage(), e);
            return ResponseEntity.status(400).body(null);
        }
    }

    /**
     * PUT /api/users/{id} - Update user
     */
    @PutMapping("/users/{id}")
    public ResponseEntity<User> updateUser(@PathVariable Long id, @RequestBody User userDetails) {
        try {
            logger.info("✏️ Updating user: {}", id);
            User updatedUser = userService.updateUser(id, userDetails);
            updatedUser.setPassword(null);
            return ResponseEntity.ok(updatedUser);
        } catch (RuntimeException e) {
            logger.warn("❌ User not found: {}", id);
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * DELETE /api/users/{id} - Delete user
     */
    @DeleteMapping("/users/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        try {
            logger.info("🗑️ Deleting user: {}", id);
            userService.deleteUser(id);
            return ResponseEntity.noContent().build();
        } catch (Exception e) {
            logger.error("❌ Error deleting user: {}", e.getMessage());
            return ResponseEntity.status(400).build();
        }
    }

    /**
     * POST /api/users/{id}/block - Block a user
     */
    @PostMapping("/users/{id}/block")
    public ResponseEntity<User> blockUser(@PathVariable Long id, @RequestParam String reason) {
        try {
            logger.info("🔒 Blocking user: {} with reason: {}", id, reason);
            User blockedUser = userService.blockUser(id, reason);
            blockedUser.setPassword(null);
            return ResponseEntity.ok(blockedUser);
        } catch (RuntimeException e) {
            logger.warn("❌ User not found: {}", id);
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * POST /api/users/{id}/unblock - Unblock a user
     */
    @PostMapping("/users/{id}/unblock")
    public ResponseEntity<User> unblockUser(@PathVariable Long id) {
        try {
            logger.info("🔓 Unblocking user: {}", id);
            User unblockedUser = userService.unblockUser(id);
            unblockedUser.setPassword(null);
            return ResponseEntity.ok(unblockedUser);
        } catch (RuntimeException e) {
            logger.warn("❌ User not found: {}", id);
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * GET /api/users/blocked - Get all blocked users
     */
    @GetMapping("/users/blocked")
    public List<User> getBlockedUsers() {
        logger.info("📋 Fetching blocked users");
        return userService.getBlockedUsers();
    }

    /**
     * GET /api/users/count - Get user count
     */
    @GetMapping("/users/count")
    public long getUserCount() {
        logger.info("📊 Counting users");
        return userService.getAllUsers().size();
    }
}