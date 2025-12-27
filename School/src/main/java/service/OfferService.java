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
        Optional<UserOffer> existingUserOffer = userOfferRepository.findByUserAndOfferAndIsActiveTrue(user, offer);
        if (existingUserOffer.isPresent()) {
            // Return the existing offer instead of throwing an exception
            return existingUserOffer.get();
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
        Optional<UserOffer> existingUserOffer = userOfferRepository.findByUserAndOfferAndIsActiveTrue(user, offer);
        if (existingUserOffer.isPresent()) {
            // Return the existing offer instead of throwing an exception
            return existingUserOffer.get();
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
    
    // Get remaining time for user's active offers
    public long getUserRemainingMinutes(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found with id: " + userId));
        
        // Get the most recent active offer
        List<UserOffer> activeOffers = userOfferRepository.findByUserAndIsActiveTrueAndApprovalStatusAndExpirationDateAfter(
                user, ApprovalStatus.APPROVED, LocalDateTime.now());
        
        if (activeOffers.isEmpty()) {
            return 0; // No active offers
        }
        
        // Find the offer with the latest expiration date
        LocalDateTime latestExpiration = activeOffers.stream()
                .map(UserOffer::getExpirationDate)
                .max(LocalDateTime::compareTo)
                .orElse(LocalDateTime.now());
        
        // Calculate remaining minutes
        long minutesUntilExpiration = java.time.Duration.between(LocalDateTime.now(), latestExpiration).toMinutes();
        return Math.max(0, minutesUntilExpiration); // Return 0 if negative
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
    
    // Get user's specific offer by email and offer ID
    public UserOffer getUserOfferByEmailAndOfferId(String email, Long offerId) {
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found with email: " + email));
        
        Offer offer = offerRepository.findById(offerId)
                .orElseThrow(() -> new RuntimeException("Offer not found with id: " + offerId));
        
        return userOfferRepository.findByUserAndOfferAndIsActiveTrue(user, offer)
                .orElse(null); // Return null if not found
    }
    
    // Get user by email
    public User getUserByEmail(String email) {
        return userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found with email: " + email));
    }
    
    // Track lesson time for a user
    public boolean trackLessonTime(Long userId, Long lessonId) {
        try {
            User user = userRepository.findById(userId)
                    .orElseThrow(() -> new RuntimeException("User not found with id: " + userId));
            
            // Find an active approved offer for this user
            List<UserOffer> activeOffers = userOfferRepository.findByUserAndIsActiveTrueAndApprovalStatusAndExpirationDateAfter(
                    user, ApprovalStatus.APPROVED, LocalDateTime.now());
            
            if (activeOffers.isEmpty()) {
                // User has no active offers, so they shouldn't be able to access lessons
                return false;
            }
            
            // In a real implementation, we would deduct time from the user's offer
            // For now, we'll just return true to indicate time tracking is successful
            // This is a simplified implementation - in a full implementation you would:
            // 1. Track the time spent on the lesson
            // 2. Deduct that time from the user's remaining time
            // 3. Update the offer's expiration date accordingly
            
            // For demonstration purposes, let's assume we're deducting 1 second
            // from the user's active offer (in a real app, you'd track actual time spent)
            
            return true;
        } catch (Exception e) {
            System.err.println("Error tracking lesson time: " + e.getMessage());
            return false;
        }
    }
}