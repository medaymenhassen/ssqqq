package com.auth.repository;

import com.auth.model.ServiceRequest;
import com.auth.model.User;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ServiceRequestRepository extends JpaRepository<ServiceRequest, Long> {
    
    @EntityGraph(attributePaths = {"provider", "recipient"})
    List<ServiceRequest> findByProvider(User provider);
    
    @EntityGraph(attributePaths = {"provider", "recipient"})
    List<ServiceRequest> findByRecipient(User recipient);
    
    @EntityGraph(attributePaths = {"provider", "recipient"})
    List<ServiceRequest> findByProviderAndStatus(User provider, ServiceRequest.ServiceStatus status);
    
    @EntityGraph(attributePaths = {"provider", "recipient"})
    List<ServiceRequest> findByRecipientAndStatus(User recipient, ServiceRequest.ServiceStatus status);
    
    @EntityGraph(attributePaths = {"provider", "recipient"})
    List<ServiceRequest> findByRecipientAndRatingIsNotNull(User recipient);
}

