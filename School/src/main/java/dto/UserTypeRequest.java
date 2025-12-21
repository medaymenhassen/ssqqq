package com.auth.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public class UserTypeRequest {
    
    @NotBlank(message = "Le nom français est obligatoire")
    @Size(max = 100, message = "Le nom français ne doit pas dépasser 100 caractères")
    private String nameFr;
    
    @NotBlank(message = "Le nom anglais est obligatoire")
    @Size(max = 100, message = "Le nom anglais ne doit pas dépasser 100 caractères")
    private String nameEn;
    
    @Size(max = 500, message = "La description française ne doit pas dépasser 500 caractères")
    private String descFr;
    
    @Size(max = 500, message = "La description anglaise ne doit pas dépasser 500 caractères")
    private String descEn;
    
    private String bigger;
    
    // Getters and Setters
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
}