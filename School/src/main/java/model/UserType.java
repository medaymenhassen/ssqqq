package com.auth.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "user_types")
public class UserType {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "name_fr", nullable = false)
    private String nameFr;
    
    @Column(name = "name_en", nullable = false)
    private String nameEn;
    
    @Column(name = "desc_fr", length = 500)
    private String descFr;
    
    @Column(name = "desc_en", length = 500)
    private String descEn;
    
    @Column(name = "bigger", nullable = false)
    private String bigger = "middle";
    
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    // Constructors
    public UserType() {}
    
    public UserType(String nameFr, String nameEn, String descFr, String descEn, String bigger) {
        this.nameFr = nameFr;
        this.nameEn = nameEn;
        this.descFr = descFr;
        this.descEn = descEn;
        this.bigger = bigger;
    }
    
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }
    
    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
    
    // Getters and Setters
    public Long getId() {
        return id;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public String getNameFr() {
        return nameFr;
    }
    
    public void setNameFr(String nameFr) {
        this.nameFr = nameFr;
    }
    
    public String getNameEn() {
        return nameEn;
    }
    
    public void setNameEn(String nameEn) {
        this.nameEn = nameEn;
    }
    
    public String getDescFr() {
        return descFr;
    }
    
    public void setDescFr(String descFr) {
        this.descFr = descFr;
    }
    
    public String getDescEn() {
        return descEn;
    }
    
    public void setDescEn(String descEn) {
        this.descEn = descEn;
    }
    
    public String getBigger() {
        return bigger;
    }
    
    public void setBigger(String bigger) {
        this.bigger = bigger;
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