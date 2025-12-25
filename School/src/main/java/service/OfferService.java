package com.auth.service;

import com.auth.model.Offer;
import com.auth.model.User;
import com.auth.model.UserOffer;
import com.auth.model.ApprovalStatus;
import com.auth.repository.OfferRepository;
import com.auth.repository.UserOfferRepository;
import com.auth.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
public class OfferService {
    
    @Autowired
    private OfferRepository offerRepository;
    
    @Autowired
    private UserOfferRepository userOfferRepository;
    
    @Autowired
    private UserRepository userRepository;
    
    // Get all active offers
    public List<Offer> getAllActiveOffers() {
        return offerRepository.findByIsActiveTrue();
    }
    
    // Get offers by user type
    public List<Offer> getOffersByUserType(Long userTypeId) {
        return offerRepository.findByUserTypeIdAndIsActiveTrue(userTypeId);
    }
    
    // Get offer by ID
    public Optional<Offer> getOfferById(Long id) {
        return offerRepository.findById(id);
    }
    
    // Create a new offer
    public Offer createOffer(Offer offer) {
        return offerRepository.save(offer);
    }
    
    // Update an existing offer
    public Offer updateOffer(Long id, Offer offerDetails) {
        Offer offer = offerRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Offer not found with id: " + id));
        
        offer.setTitle(offerDetails.getTitle());
        offer.setDescription(offerDetails.getDescription());
        offer.setPrice(offerDetails.getPrice());
        offer.setDurationHours(offerDetails.getDurationHours());
        offer.setUserTypeId(offerDetails.getUserTypeId());
        offer.setIsActive(offerDetails.getIsActive());
        
        return offerRepository.save(offer);
    }
    
    // Delete an offer
    public void deleteOffer(Long id) {
        Offer offer = offerRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Offer not found with id: " + id));
        offerRepository.delete(offer);
    }
    
    // Purchase an offer for a user
    public UserOffer purchaseOffer(Long userId, Long offerId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found with id: " + userId));
        
        Offer offer = offerRepository.findById(offerId)
                .orElseThrow(() -> new RuntimeException("Offer not found with id: " + offerId));
        
        // Check if user already has this offer
        if (userOfferRepository.existsByUserAndOfferAndIsActiveTrue(user, offer)) {
            throw new RuntimeException("User already has this offer");
        }
        
        LocalDateTime purchaseDate = LocalDateTime.now();
        LocalDateTime expirationDate = purchaseDate.plusHours(offer.getDurationHours());
        
        UserOffer userOffer = new UserOffer(user, offer, purchaseDate, expirationDate);
        // By default, new purchases are in PENDING status awaiting admin approval
        return userOfferRepository.save(userOffer);
    }
    
    // Purchase an offer for a user by email
    public UserOffer purchaseOfferByEmail(String email, Long offerId) {
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found with email: " + email));
        
        Offer offer = offerRepository.findById(offerId)
                .orElseThrow(() -> new RuntimeException("Offer not found with id: " + offerId));
        
        // Check if user already has this offer
        if (userOfferRepository.existsByUserAndOfferAndIsActiveTrue(user, offer)) {
            throw new RuntimeException("User already has this offer");
        }
        
        LocalDateTime purchaseDate = LocalDateTime.now();
        LocalDateTime expirationDate = purchaseDate.plusHours(offer.getDurationHours());
        
        UserOffer userOffer = new UserOffer(user, offer, purchaseDate, expirationDate);
        // By default, new purchases are in PENDING status awaiting admin approval
        return userOfferRepository.save(userOffer);
    }
    
    // Approve a user's offer access
    public UserOffer approveOffer(Long userOfferId) {
        UserOffer userOffer = userOfferRepository.findById(userOfferId)
                .orElseThrow(() -> new RuntimeException("UserOffer not found with id: " + userOfferId));
        
        userOffer.setApprovalStatus(ApprovalStatus.APPROVED);
        userOffer.setIsActive(true); // Enable access after approval
        return userOfferRepository.save(userOffer);
    }
    
    // Reject a user's offer access
    public UserOffer rejectOffer(Long userOfferId) {
        UserOffer userOffer = userOfferRepository.findById(userOfferId)
                .orElseThrow(() -> new RuntimeException("UserOffer not found with id: " + userOfferId));
        
        userOffer.setApprovalStatus(ApprovalStatus.REJECTED);
        userOffer.setIsActive(false); // Disable access if rejected
        return userOfferRepository.save(userOffer);
    }
    
    // Check if user has access to content based on approved offers
    public boolean userHasAccessToContent(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found with id: " + userId));
        
        // Check if user has any approved and active offers that haven't expired
        List<UserOffer> activeOffers = userOfferRepository.findByUserAndIsActiveTrueAndApprovalStatusAndExpirationDateAfter(
                user, ApprovalStatus.APPROVED, LocalDateTime.now());
        
        return !activeOffers.isEmpty();
    }
    
    // Get user's pending offers (awaiting approval)
    public List<UserOffer> getUserPendingOffers(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found with id: " + userId));
        
        return userOfferRepository.findByUserAndApprovalStatus(user, ApprovalStatus.PENDING);
    }
    
    // Get user's approved offers
    public List<UserOffer> getUserApprovedOffers(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found with id: " + userId));
        
        return userOfferRepository.findByUserAndApprovalStatus(user, ApprovalStatus.APPROVED);
    }
    
    // Get user's rejected offers
    public List<UserOffer> getUserRejectedOffers(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found with id: " + userId));
        
        return userOfferRepository.findByUserAndApprovalStatus(user, ApprovalStatus.REJECTED);
    }
    

    
    // Get user's purchased offers
    public List<UserOffer> getUserPurchasedOffers(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found with id: " + userId));
        
        return userOfferRepository.findByUserAndIsActiveTrue(user);
    }
}