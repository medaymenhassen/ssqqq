package com.auth.repository;

import com.auth.model.UserOffer;
import com.auth.model.User;
import com.auth.model.Offer;
import com.auth.model.ApprovalStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface UserOfferRepository extends JpaRepository<UserOffer, Long> {
    List<UserOffer> findByUser(User user);
    List<UserOffer> findByUserAndIsActiveTrue(User user);
    List<UserOffer> findByUserAndIsActiveTrueAndExpirationDateAfter(User user, LocalDateTime currentDate);
    Optional<UserOffer> findByUserAndOfferAndIsActiveTrue(User user, Offer offer);
    boolean existsByUserAndOfferAndIsActiveTrue(User user, Offer offer);
    
    // New methods for approval status
    List<UserOffer> findByUserAndApprovalStatus(User user, ApprovalStatus approvalStatus);
    List<UserOffer> findByUserAndIsActiveTrueAndApprovalStatusAndExpirationDateAfter(User user, ApprovalStatus approvalStatus, LocalDateTime currentDate);
}