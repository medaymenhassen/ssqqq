package com.auth.controller;

import com.auth.model.Offer;
import com.auth.model.UserOffer;
import com.auth.service.OfferService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import com.auth.model.User;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/offers")
@CrossOrigin(origins = {"http://localhost:4200", "https://cognitiex.com"})
public class OfferController {
    
    @Autowired
    private OfferService offerService;
    
    @Autowired
    private org.springframework.security.core.userdetails.UserDetailsService userDetailsService;
    
    // Get all active offers
    @GetMapping
    public List<Offer> getAllActiveOffers() {
        return offerService.getAllActiveOffers();
    }
    
    // Get offer by ID
    @GetMapping("/{id}")
    public ResponseEntity<Offer> getOfferById(@PathVariable Long id) {
        return offerService.getOfferById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
    
    // Create a new offer (admin users only)
    @PostMapping
    public Offer createOffer(@RequestBody Offer offer) {

        
        return offerService.createOffer(offer);
    }
    
    // Update an offer (authenticated users only - temporary)
    @PutMapping("/{id}")
    @PreAuthorize("isAuthenticated()")
    public ResponseEntity<Offer> updateOffer(@PathVariable Long id, @RequestBody Offer offerDetails) {
        try {
            Offer updatedOffer = offerService.updateOffer(id, offerDetails);
            return ResponseEntity.ok(updatedOffer);
        } catch (RuntimeException e) {
            return ResponseEntity.notFound().build();
        }
    }
    
    // Delete an offer (authenticated users only - temporary)
    @DeleteMapping("/{id}")
    @PreAuthorize("isAuthenticated()")
    public ResponseEntity<Void> deleteOffer(@PathVariable Long id) {
        try {
            offerService.deleteOffer(id);
            return ResponseEntity.noContent().build();
        } catch (RuntimeException e) {
            return ResponseEntity.notFound().build();
        }
    }
    
    // Purchase an offer
    @PostMapping("/{offerId}/purchase")
    @PreAuthorize("hasRole('USER') or hasRole('ADMIN')")
    public ResponseEntity<Object> purchaseOffer(@PathVariable Long offerId) {
        try {
            // Get the authenticated user from security context
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            if (authentication == null || !authentication.isAuthenticated()) {
                return ResponseEntity.status(401).body(Map.of("error", "User not authenticated"));
            }
            String email = authentication.getName();
            
            // Use the email to purchase the offer directly
            UserOffer userOffer = offerService.purchaseOfferByEmail(email, offerId);
            return ResponseEntity.ok(userOffer);
        } catch (Exception e) {
            // Always return JSON object, not string
            return ResponseEntity.badRequest().body(Map.of("error", "Could not purchase offer: " + e.getMessage()));
        }
    }
    
    // Check if user has access to content
    @GetMapping("/user/{userId}/access")
    public ResponseEntity<Boolean> userHasAccess(@PathVariable Long userId) {
        boolean hasAccess = offerService.userHasAccessToContent(userId);
        return ResponseEntity.ok(hasAccess);
    }
    
    // Get user's pending offers (awaiting admin approval)
    @GetMapping("/user/{userId}/pending")
    @PreAuthorize("hasRole('USER') or hasRole('ADMIN')")
    public ResponseEntity<Object> getUserPendingOffers(@PathVariable Long userId) {
        try {
            // Verify authentication and user context
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            if (authentication == null || !authentication.isAuthenticated()) {
                return ResponseEntity.status(401)
                    .body(Map.of("error", "User not authenticated"));
            }
            
            String email = authentication.getName();
            User authenticatedUser = offerService.getUserByEmail(email);
            
            // Check if user is admin or requesting their own data
            boolean isAdmin = authentication.getAuthorities()
                .stream().anyMatch(auth -> auth.getAuthority().equals("ROLE_ADMIN"));
            
            if (!authenticatedUser.getId().equals(userId) && !isAdmin) {
                return ResponseEntity.status(403)
                    .body(Map.of("error", "Access denied: Cannot view other users' offers"));
            }
            
            List<UserOffer> userOffers = offerService.getUserPendingOffers(userId);
            return ResponseEntity.ok(userOffers);
            
        } catch (RuntimeException e) {
            return ResponseEntity.status(404)
                .body(Map.of("error", "User not found: " + e.getMessage()));
        }
    }
    
    // Get user's approved offers
    @GetMapping("/user/{userId}/approved")
    @PreAuthorize("hasRole('USER') or hasRole('ADMIN')")
    public ResponseEntity<Object> getUserApprovedOffers(@PathVariable Long userId) {
        try {
            // Verify authentication and user context
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            if (authentication == null || !authentication.isAuthenticated()) {
                return ResponseEntity.status(401)
                    .body(Map.of("error", "User not authenticated"));
            }
            
            String email = authentication.getName();
            User authenticatedUser = offerService.getUserByEmail(email);
            
            // Check if user is admin or requesting their own data
            boolean isAdmin = authentication.getAuthorities()
                .stream().anyMatch(auth -> auth.getAuthority().equals("ROLE_ADMIN"));
            
            if (!authenticatedUser.getId().equals(userId) && !isAdmin) {
                return ResponseEntity.status(403)
                    .body(Map.of("error", "Access denied: Cannot view other users' offers"));
            }
            
            List<UserOffer> userOffers = offerService.getUserApprovedOffers(userId);
            return ResponseEntity.ok(userOffers);
            
        } catch (RuntimeException e) {
            return ResponseEntity.status(404)
                .body(Map.of("error", "User not found: " + e.getMessage()));
        }
    }
    
    // Get user's rejected offers
    @GetMapping("/user/{userId}/rejected")
    @PreAuthorize("hasRole('USER') or hasRole('ADMIN')")
    public ResponseEntity<Object> getUserRejectedOffers(@PathVariable Long userId) {
        try {
            // Verify authentication and user context
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            if (authentication == null || !authentication.isAuthenticated()) {
                return ResponseEntity.status(401)
                    .body(Map.of("error", "User not authenticated"));
            }
            
            String email = authentication.getName();
            User authenticatedUser = offerService.getUserByEmail(email);
            
            // Check if user is admin or requesting their own data
            boolean isAdmin = authentication.getAuthorities()
                .stream().anyMatch(auth -> auth.getAuthority().equals("ROLE_ADMIN"));
            
            if (!authenticatedUser.getId().equals(userId) && !isAdmin) {
                return ResponseEntity.status(403)
                    .body(Map.of("error", "Access denied: Cannot view other users' offers"));
            }
            
            List<UserOffer> userOffers = offerService.getUserRejectedOffers(userId);
            return ResponseEntity.ok(userOffers);
            
        } catch (RuntimeException e) {
            return ResponseEntity.status(404)
                .body(Map.of("error", "User not found: " + e.getMessage()));
        }
    }
    
    // Admin approve an offer
    @PutMapping("/{userOfferId}/approve")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<UserOffer> approveOffer(@PathVariable Long userOfferId) {
        try {
            UserOffer userOffer = offerService.approveOffer(userOfferId);
            return ResponseEntity.ok(userOffer);
        } catch (RuntimeException e) {
            return ResponseEntity.notFound().build();
        }
    }
    
    // Admin reject an offer
    @PutMapping("/{userOfferId}/reject")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<UserOffer> rejectOffer(@PathVariable Long userOfferId) {
        try {
            UserOffer userOffer = offerService.rejectOffer(userOfferId);
            return ResponseEntity.ok(userOffer);
        } catch (RuntimeException e) {
            return ResponseEntity.notFound().build();
        }
    }
    
    // Get user's purchased offers
    @GetMapping("/user/{userId}/purchases")
    @PreAuthorize("hasRole('USER') or hasRole('ADMIN')")
    public ResponseEntity<Object> getUserPurchasedOffers(@PathVariable Long userId) {
        try {
            // Verify authentication and user context
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            if (authentication == null || !authentication.isAuthenticated()) {
                return ResponseEntity.status(401)
                    .body(Map.of("error", "User not authenticated"));
            }
            
            String email = authentication.getName();
            User authenticatedUser = offerService.getUserByEmail(email);
            
            // Check if user is admin or requesting their own data
            boolean isAdmin = authentication.getAuthorities()
                .stream().anyMatch(auth -> auth.getAuthority().equals("ROLE_ADMIN"));
            
            if (!authenticatedUser.getId().equals(userId) && !isAdmin) {
                return ResponseEntity.status(403)
                    .body(Map.of("error", "Access denied: Cannot view other users' offers"));
            }
            
            List<UserOffer> userOffers = offerService.getUserPurchasedOffers(userId);
            return ResponseEntity.ok(userOffers);
            
        } catch (RuntimeException e) {
            return ResponseEntity.status(404)
                .body(Map.of("error", "User not found: " + e.getMessage()));
        }
    }
    
    // Track lesson time for a user
    @PostMapping("/user/{userId}/track-lesson/{lessonId}")
    @PreAuthorize("hasRole('USER') or hasRole('ADMIN')")
    public ResponseEntity<Object> trackLessonTime(@PathVariable Long userId, @PathVariable Long lessonId) {
        try {
            // Get the authenticated user from security context
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            if (authentication == null || !authentication.isAuthenticated()) {
                return ResponseEntity.status(401).body(Map.of("error", "User not authenticated"));
            }
            String email = authentication.getName();
            
            // Verify that the authenticated user matches the requested userId
            User authenticatedUser = offerService.getUserByEmail(email);
            if (authenticatedUser == null || !authenticatedUser.getId().equals(userId)) {
                return ResponseEntity.status(403).body(Map.of("error", "Access denied"));
            }
            
            // Track lesson time and deduct from user's offer
            boolean success = offerService.trackLessonTime(userId, lessonId);
            if (success) {
                return ResponseEntity.ok(Map.of("message", "Lesson time tracked successfully"));
            } else {
                return ResponseEntity.status(400).body(Map.of("error", "Failed to track lesson time"));
            }
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("error", "Could not track lesson time: " + e.getMessage()));
        }
    }
    
    // Get user's remaining time
    @GetMapping("/user/{userId}/remaining-time")
    @PreAuthorize("hasRole('USER') or hasRole('ADMIN')")
    public ResponseEntity<Object> getUserRemainingTime(@PathVariable Long userId) {
        try {
            // Get the authenticated user from security context
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            if (authentication == null || !authentication.isAuthenticated()) {
                return ResponseEntity.status(401).body(Map.of("error", "User not authenticated"));
            }
            String email = authentication.getName();
            
            // Verify that the authenticated user matches the requested userId
            User authenticatedUser = offerService.getUserByEmail(email);
            if (authenticatedUser == null || !authenticatedUser.getId().equals(userId)) {
                return ResponseEntity.status(403).body(Map.of("error", "Access denied"));
            }
            
            // Get remaining time in minutes
            long remainingMinutes = offerService.getUserRemainingMinutes(userId);
            return ResponseEntity.ok(Map.of("remainingMinutes", remainingMinutes));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("error", "Could not get remaining time: " + e.getMessage()));
        }
    }
}