package com.auth.model;

public enum CalendarEventType {
    TRAINING("Formation"),
    MEETING("Réunion"),
    AVAILABLE_SLOT("Créneau disponible");
    
    private final String displayName;
    
    CalendarEventType(String displayName) {
        this.displayName = displayName;
    }
    
    public String getDisplayName() {
        return displayName;
    }
}

