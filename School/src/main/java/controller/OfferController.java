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
    public ResponseEntity<?> purchaseOffer(@PathVariable Long offerId) {
        try {
            // Get the authenticated user from security context
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            String email = authentication.getName();
            
            // Use the email to purchase the offer directly
            UserOffer userOffer = offerService.purchaseOfferByEmail(email, offerId);
            return ResponseEntity.ok(userOffer);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body("Could not purchase offer: " + e.getMessage());
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
    public ResponseEntity<List<UserOffer>> getUserPendingOffers(@PathVariable Long userId) {
        try {
            List<UserOffer> userOffers = offerService.getUserPendingOffers(userId);
            return ResponseEntity.ok(userOffers);
        } catch (RuntimeException e) {
            return ResponseEntity.notFound().build();
        }
    }
    
    // Get user's approved offers
    @GetMapping("/user/{userId}/approved")
    @PreAuthorize("hasRole('USER') or hasRole('ADMIN')")
    public ResponseEntity<List<UserOffer>> getUserApprovedOffers(@PathVariable Long userId) {
        try {
            List<UserOffer> userOffers = offerService.getUserApprovedOffers(userId);
            return ResponseEntity.ok(userOffers);
        } catch (RuntimeException e) {
            return ResponseEntity.notFound().build();
        }
    }
    
    // Get user's rejected offers
    @GetMapping("/user/{userId}/rejected")
    @PreAuthorize("hasRole('USER') or hasRole('ADMIN')")
    public ResponseEntity<List<UserOffer>> getUserRejectedOffers(@PathVariable Long userId) {
        try {
            List<UserOffer> userOffers = offerService.getUserRejectedOffers(userId);
            return ResponseEntity.ok(userOffers);
        } catch (RuntimeException e) {
            return ResponseEntity.notFound().build();
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
    public ResponseEntity<List<UserOffer>> getUserPurchasedOffers(@PathVariable Long userId) {
        try {
            List<UserOffer> userOffers = offerService.getUserPurchasedOffers(userId);
            return ResponseEntity.ok(userOffers);
        } catch (RuntimeException e) {
            return ResponseEntity.notFound().build();
        }
    }
}