package com.auth.repository;

import com.auth.model.UserOffer;
import com.auth.model.User;
import com.auth.model.Offer;
import com.auth.model.ApprovalStatus;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface UserOfferRepository extends JpaRepository<UserOffer, Long> {
    @EntityGraph(attributePaths = {"user", "offer"})
    List<UserOffer> findByUser(User user);
    
    @EntityGraph(attributePaths = {"user", "offer"})
    List<UserOffer> findByUserAndIsActiveTrue(User user);
    
    @EntityGraph(attributePaths = {"user", "offer"})
    List<UserOffer> findByUserAndIsActiveTrueAndExpirationDateAfter(User user, LocalDateTime currentDate);
    
    @EntityGraph(attributePaths = {"user", "offer"})
    Optional<UserOffer> findByUserAndOfferAndIsActiveTrue(User user, Offer offer);
    
    boolean existsByUserAndOfferAndIsActiveTrue(User user, Offer offer);
    
    // New methods for approval status
    @EntityGraph(attributePaths = {"user", "offer"})
    List<UserOffer> findByUserAndApprovalStatus(User user, ApprovalStatus approvalStatus);
    
    @EntityGraph(attributePaths = {"user", "offer"})
    List<UserOffer> findByUserAndIsActiveTrueAndApprovalStatusAndExpirationDateAfter(User user, ApprovalStatus approvalStatus, LocalDateTime currentDate);
}