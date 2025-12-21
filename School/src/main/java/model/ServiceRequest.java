package com.auth.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;

@Entity
@Table(name = "service_requests")
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class ServiceRequest {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @NotNull
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "provider_id", nullable = false)
    @JsonIgnoreProperties({"hibernateLazyInitializer", "handler", "password"})
    private User provider; // Celui qui fournit la prestation
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "recipient_id", nullable = true)
    @JsonIgnoreProperties({"hibernateLazyInitializer", "handler", "password"})
    private User recipient; // Celui qui reçoit la prestation (null si proposition ouverte à tous)
    
    @NotNull
    @Size(max = 255)
    @Column(nullable = false)
    private String title; // Titre de la prestation
    
    @Size(max = 1000)
    @Column(length = 1000)
    private String description; // Description de la prestation
    
    @NotNull
    @Column(name = "service_type", nullable = false)
    @Enumerated(EnumType.STRING)
    private ServiceType serviceType; // Type de prestation
    
    @Column(name = "status")
    @Enumerated(EnumType.STRING)
    private ServiceStatus status = ServiceStatus.PENDING; // Statut de la prestation
    
    @Column(name = "is_open_to_all")
    private Boolean isOpenToAll = false; // Si true, la proposition est ouverte à tous (recipient null)
    
    @Column(name = "rating")
    private Integer rating; // Note de 1 à 5 (peut être null si pas encore noté)
    
    @Size(max = 2000)
    @Column(name = "comment", length = 2000)
    private String comment; // Commentaire du receveur
    
    @Column(name = "completed_at")
    private LocalDateTime completedAt; // Date de complétion de la prestation
    
    @Column(name = "rated_at")
    private LocalDateTime ratedAt; // Date de notation
    
    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    // Enums
    public enum ServiceType {
        COURSE_CREATED,      // Cours créé
        FREELANCE_MISSION,   // Mission freelance
        TUTORING,            // Tutorat
        CONSULTING,          // Conseil
        OTHER                // Autre
    }
    
    public enum ServiceStatus {
        PENDING,     // En attente
        IN_PROGRESS, // En cours
        COMPLETED,   // Complété
        CANCELLED    // Annulé
    }
    
    // Constructors
    public ServiceRequest() {}
    
    public ServiceRequest(User provider, User recipient, String title, ServiceType serviceType) {
        this.provider = provider;
        this.recipient = recipient;
        this.title = title;
        this.serviceType = serviceType;
    }
    
    // Getters and Setters
    public Long getId() {
        return id;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public User getProvider() {
        return provider;
    }
    
    public void setProvider(User provider) {
        this.provider = provider;
    }
    
    public User getRecipient() {
        return recipient;
    }
    
    public void setRecipient(User recipient) {
        this.recipient = recipient;
    }
    
    public String getTitle() {
        return title;
    }
    
    public void setTitle(String title) {
        this.title = title;
    }
    
    public String getDescription() {
        return description;
    }
    
    public void setDescription(String description) {
        this.description = description;
    }
    
    public ServiceType getServiceType() {
        return serviceType;
    }
    
    public void setServiceType(ServiceType serviceType) {
        this.serviceType = serviceType;
    }
    
    public ServiceStatus getStatus() {
        return status;
    }
    
    public void setStatus(ServiceStatus status) {
        this.status = status;
    }
    
    public Integer getRating() {
        return rating;
    }
    
    public void setRating(Integer rating) {
        this.rating = rating;
        if (rating != null) {
            this.ratedAt = LocalDateTime.now();
        }
    }
    
    public String getComment() {
        return comment;
    }
    
    public void setComment(String comment) {
        this.comment = comment;
    }
    
    public LocalDateTime getCompletedAt() {
        return completedAt;
    }
    
    public void setCompletedAt(LocalDateTime completedAt) {
        this.completedAt = completedAt;
    }
    
    public LocalDateTime getRatedAt() {
        return ratedAt;
    }
    
    public void setRatedAt(LocalDateTime ratedAt) {
        this.ratedAt = ratedAt;
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
    
    public Boolean getIsOpenToAll() {
        return isOpenToAll;
    }
    
    public void setIsOpenToAll(Boolean isOpenToAll) {
        this.isOpenToAll = isOpenToAll;
    }
}

