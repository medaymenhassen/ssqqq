package com.auth.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public class UserTypeRequest {
    
    @NotBlank(message = "Le nom est obligatoire")
    @Size(max = 100, message = "Le nom ne doit pas dépasser 100 caractères")
    private String nom;
    
    @Size(max = 500, message = "La description ne doit pas dépasser 500 caractères")
    private String description;
    
    private boolean isSpecial;
    
    // Getters and Setters
    public String getNom() {
        return nom;
    }
    
    public void setNom(String nom) {
        this.nom = nom;
    }
    
    public String getDescription() {
        return description;
    }
    
    public void setDescription(String description) {
        this.description = description;
    }
    
    public boolean isSpecial() {
        return isSpecial;
    }
    
    public void setSpecial(boolean special) {
        isSpecial = special;
    }
}