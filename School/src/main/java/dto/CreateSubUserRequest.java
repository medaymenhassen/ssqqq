package com.cognitiex.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public class CreateSubUserRequest {
    
    @NotBlank(message = "Le prénom est obligatoire")
    @Size(max = 100, message = "Le prénom ne peut pas dépasser 100 caractères")
    private String firstName;
    
    @NotBlank(message = "Le nom est obligatoire")
    @Size(max = 100, message = "Le nom ne peut pas dépasser 100 caractères")
    private String lastName;
    
    @NotBlank(message = "Le poste/travail est obligatoire")
    @Size(max = 100, message = "Le poste ne peut pas dépasser 100 caractères")
    private String job;
    
    @NotBlank(message = "Le niveau est obligatoire")
    @Size(max = 50, message = "Le niveau ne peut pas dépasser 50 caractères")
    private String level;
    
    public CreateSubUserRequest() {}
    
    public CreateSubUserRequest(String firstName, String lastName, String job, String level) {
        this.firstName = firstName;
        this.lastName = lastName;
        this.job = job;
        this.level = level;
    }
    
    public String getFirstName() {
        return firstName;
    }
    
    public void setFirstName(String firstName) {
        this.firstName = firstName;
    }
    
    public String getLastName() {
        return lastName;
    }
    
    public void setLastName(String lastName) {
        this.lastName = lastName;
    }
    
    public String getJob() {
        return job;
    }
    
    public void setJob(String job) {
        this.job = job;
    }
    
    public String getLevel() {
        return level;
    }
    
    public void setLevel(String level) {
        this.level = level;
    }
}

