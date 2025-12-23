package com.auth.controller;

import com.auth.model.Offer;
import com.auth.model.UserOffer;
import com.auth.service.OfferService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/offers")
@CrossOrigin(origins = {"http://localhost:4200", "https://cognitiex.com"})
public class OfferController {
    
    @Autowired
    private OfferService offerService;
    
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
    
    // Create a new offer (public - no authentication required)
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
    public ResponseEntity<?> purchaseOffer(@PathVariable Long offerId, @RequestParam Long userId) {
        try {
            UserOffer userOffer = offerService.purchaseOffer(userId, offerId);
            return ResponseEntity.ok(userOffer);
        } catch (RuntimeException e) {
            return ResponseEntity.badRequest().body(e.getMessage());
        }
    }
    
    // Check if user has access to content
    @GetMapping("/user/{userId}/access")
    public ResponseEntity<Boolean> userHasAccess(@PathVariable Long userId) {
        boolean hasAccess = offerService.userHasAccessToContent(userId);
        return ResponseEntity.ok(hasAccess);
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