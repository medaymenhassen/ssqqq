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
        System.out.println("📥 [OFFER CREATION] RECEIVED from frontend:");
        System.out.println("   Full Offer: " + offer);
        System.out.println("   Expected fields from Offer model:");
        System.out.println("   - id: Long (will be set by backend)");
        System.out.println("   - title: String (required)");
        System.out.println("   - description: String (optional)");
        System.out.println("   - price: BigDecimal (required)");
        System.out.println("   - durationHours: Integer (required)");
        System.out.println("   - userTypeId: Long (foreign key to UserType, optional)");
        System.out.println("   - isActive: Boolean (required, default true)");
        System.out.println("   - createdAt: LocalDateTime (set by backend)");
        System.out.println("   - updatedAt: LocalDateTime (set by backend)");
        System.out.println("\n   Received values:");
        System.out.println("   - title: '" + offer.getTitle() + "' (type: " + (offer.getTitle() != null ? offer.getTitle().getClass().getSimpleName() : "null") + ")");
        System.out.println("   - description: '" + offer.getDescription() + "' (type: " + (offer.getDescription() != null ? offer.getDescription().getClass().getSimpleName() : "null") + ")");
        System.out.println("   - price: " + offer.getPrice() + " (type: " + (offer.getPrice() != null ? offer.getPrice().getClass().getSimpleName() : "null") + ")");
        System.out.println("   - durationHours: " + offer.getDurationHours() + " (type: " + (offer.getDurationHours() != null ? offer.getDurationHours().getClass().getSimpleName() : "null") + ")");
        System.out.println("   - userTypeId: " + offer.getUserTypeId() + " (type: " + (offer.getUserTypeId() != null ? offer.getUserTypeId().getClass().getSimpleName() : "null") + ")");
        System.out.println("   - isActive: " + offer.getIsActive() + " (type: " + (offer.getIsActive() != null ? offer.getIsActive().getClass().getSimpleName() : "null") + ")");
        
        return offerService.createOffer(offer);
    }
    
    // Update an offer (admin only)
    @PutMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Offer> updateOffer(@PathVariable Long id, @RequestBody Offer offerDetails) {
        try {
            Offer updatedOffer = offerService.updateOffer(id, offerDetails);
            return ResponseEntity.ok(updatedOffer);
        } catch (RuntimeException e) {
            return ResponseEntity.notFound().build();
        }
    }
    
    // Delete an offer (admin only)
    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
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