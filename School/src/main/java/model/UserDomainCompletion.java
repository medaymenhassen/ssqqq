package com.auth.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;

@Entity
@Table(name = "user_domain_completions", uniqueConstraints = {
    @UniqueConstraint(columnNames = {"user_id", "domain_id"})
})
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class UserDomainCompletion {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    @JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
    private User user;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "domain_id", nullable = false)
    @JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
    private TrainingDomain domain;
    
    @Column(name = "completed_at", nullable = false)
    private LocalDateTime completedAt;
    
    @Column(name = "is_free_access")
    private Boolean isFreeAccess = true; // Le domaine devient gratuit après complétion
    
    @Column(name = "domain_link", length = 500)
    private String domainLink; // Lien du domaine (visible dans le profil)
    
    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    // Constructors
    public UserDomainCompletion() {}
    
    public UserDomainCompletion(User user, TrainingDomain domain) {
        this.user = user;
        this.domain = domain;
        this.completedAt = LocalDateTime.now();
        this.isFreeAccess = true;
        this.domainLink = "/programs/" + domain.getSlug();
    }
    
    // Getters and Setters
    public Long getId() {
        return id;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public User getUser() {
        return user;
    }
    
    public void setUser(User user) {
        this.user = user;
    }
    
    public TrainingDomain getDomain() {
        return domain;
    }
    
    public void setDomain(TrainingDomain domain) {
        this.domain = domain;
    }
    
    public LocalDateTime getCompletedAt() {
        return completedAt;
    }
    
    public void setCompletedAt(LocalDateTime completedAt) {
        this.completedAt = completedAt;
    }
    
    public Boolean getIsFreeAccess() {
        return isFreeAccess;
    }
    
    public void setIsFreeAccess(Boolean isFreeAccess) {
        this.isFreeAccess = isFreeAccess;
    }
    
    public String getDomainLink() {
        return domainLink;
    }
    
    public void setDomainLink(String domainLink) {
        this.domainLink = domainLink;
    }
    
    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
    
    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
    
    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }
    
    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }
}

