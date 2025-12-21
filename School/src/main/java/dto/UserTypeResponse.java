package com.auth.dto;

import java.time.LocalDateTime;

public class UserTypeResponse {
    
    private Long id;
    private String nameFr;
    private String nameEn;
    private String descFr;
    private String descEn;
    private String bigger;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    
    // Constructors
    public UserTypeResponse() {}
    
    public UserTypeResponse(Long id, String nameFr, String nameEn, String descFr, String descEn, String bigger, LocalDateTime createdAt, LocalDateTime updatedAt) {
        this.id = id;
        this.nameFr = nameFr;
        this.nameEn = nameEn;
        this.descFr = descFr;
        this.descEn = descEn;
        this.bigger = bigger;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
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