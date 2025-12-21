package com.auth.model;

import jakarta.persistence.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;

@Entity
public class UserTypeDefinitionBackup {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "type_code", nullable = false, unique = true)
    private String typeCode;
    
    @Column(name = "label_fr", nullable = false)
    private String labelFr;
    
    @Column(name = "label_en", nullable = false)
    private String labelEn;
    
    @Column(name = "description_fr", length = 500)
    private String descriptionFr;
    
    @Column(name = "description_en", length = 500)
    private String descriptionEn;
    
    @Column(name = "is_active")
    private Boolean isActive = true;
    
    @Column(name = "display_order")
    private Integer displayOrder = 0;
    
    @Column(name = "show_in_selection")
    private Boolean showInSelection = true;
    
    @Column(name = "bigger", nullable = false)
    private String bigger = "middle";
    
    @Column(name = "company_type")
    private String companyType;
    
    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    // Constructors
    public UserTypeDefinitionBackup() {}
    
    public UserTypeDefinitionBackup(String typeCode, String labelFr, String labelEn) {
        this.typeCode = typeCode;
        this.labelFr = labelFr;
        this.labelEn = labelEn;
    }
    
    // Getters and Setters
    public Long getId() {
        return id;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public String getTypeCode() {
        return typeCode;
    }
    
    public void setTypeCode(String typeCode) {
        this.typeCode = typeCode;
    }
    
    public String getLabelFr() {
        return labelFr;
    }
    
    public void setLabelFr(String labelFr) {
        this.labelFr = labelFr;
    }
    
    public String getLabelEn() {
        return labelEn;
    }
    
    public void setLabelEn(String labelEn) {
        this.labelEn = labelEn;
    }
    
    public String getDescriptionFr() {
        return descriptionFr;
    }
    
    public void setDescriptionFr(String descriptionFr) {
        this.descriptionFr = descriptionFr;
    }
    
    public String getDescriptionEn() {
        return descriptionEn;
    }
    
    public void setDescriptionEn(String descriptionEn) {
        this.descriptionEn = descriptionEn;
    }
    
    public Boolean getIsActive() {
        return isActive;
    }
    
    public void setIsActive(Boolean isActive) {
        this.isActive = isActive;
    }
    
    public Integer getDisplayOrder() {
        return displayOrder;
    }
    
    public void setDisplayOrder(Integer displayOrder) {
        this.displayOrder = displayOrder;
    }
    
    public Boolean getShowInSelection() {
        return showInSelection;
    }
    
    public void setShowInSelection(Boolean showInSelection) {
        this.showInSelection = showInSelection;
    }
    
    public String getBigger() {
        return bigger;
    }
    
    public void setBigger(String bigger) {
        this.bigger = bigger;
    }
    
    public String getCompanyType() {
        return companyType;
    }
    
    public void setCompanyType(String companyType) {
        this.companyType = companyType;
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

