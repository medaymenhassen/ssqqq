package com.auth.model;

public enum MeetingRequestStatus {
    PENDING("En attente"),
    APPROVED("Approuvé"),
    RESCHEDULED("Reprogrammé"),
    REJECTED("Refusé"),
    CANCELLED("Annulé");
    
    private final String displayName;
    
    MeetingRequestStatus(String displayName) {
        this.displayName = displayName;
    }
    
    public String getDisplayName() {
        return displayName;
    }
}

