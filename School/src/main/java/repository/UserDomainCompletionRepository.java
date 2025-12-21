package com.auth.repository;

import com.auth.model.TrainingDomain;
import com.auth.model.User;
import com.auth.model.UserDomainCompletion;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface UserDomainCompletionRepository extends JpaRepository<UserDomainCompletion, Long> {
    @EntityGraph(attributePaths = {"user", "domain"})
    Optional<UserDomainCompletion> findByUserAndDomain(User user, TrainingDomain domain);
    
    @EntityGraph(attributePaths = {"user", "domain"})
    @Query("SELECT udc FROM UserDomainCompletion udc WHERE udc.user = ?1")
    List<UserDomainCompletion> findByUser(User user);
    
    @EntityGraph(attributePaths = {"user", "domain"})
    List<UserDomainCompletion> findByDomain(TrainingDomain domain);
    
    boolean existsByUserAndDomain(User user, TrainingDomain domain);
}

