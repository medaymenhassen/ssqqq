package com.auth.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;

@Entity
@Table(name = "company_calendars")
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class CompanyCalendar {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @NotNull
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "company_id", nullable = false)
    @JsonIgnoreProperties({"hibernateLazyInitializer", "handler", "password"})
    private User company; // L'entreprise propriétaire de l'agenda
    
    @NotBlank
    @Size(max = 255)
    @Column(nullable = false)
    private String title;
    
    @Size(max = 1000)
    @Column(length = 1000)
    private String description;
    
    @NotNull
    @Column(name = "start_time", nullable = false)
    private LocalDateTime startTime;
    
    @NotNull
    @Column(name = "end_time", nullable = false)
    private LocalDateTime endTime;
    
    @Column(name = "event_type")
    @Enumerated(EnumType.STRING)
    private CalendarEventType eventType = CalendarEventType.TRAINING; // TRAINING, MEETING, AVAILABLE_SLOT
    
    @Column(name = "is_available")
    private Boolean isAvailable = true; // Si false, le créneau est occupé
    
    @Column(name = "meeting_link")
    @Size(max = 500)
    private String meetingLink; // Lien Google Meet, Zoom, etc.
    
    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    // Constructors
    public CompanyCalendar() {}
    
    public CompanyCalendar(User company, String title, LocalDateTime startTime, LocalDateTime endTime) {
        this.company = company;
        this.title = title;
        this.startTime = startTime;
        this.endTime = endTime;
    }
    
    // Getters and Setters
    public Long getId() {
        return id;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public User getCompany() {
        return company;
    }
    
    public void setCompany(User company) {
        this.company = company;
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
    
    public LocalDateTime getStartTime() {
        return startTime;
    }
    
    public void setStartTime(LocalDateTime startTime) {
        this.startTime = startTime;
    }
    
    public LocalDateTime getEndTime() {
        return endTime;
    }
    
    public void setEndTime(LocalDateTime endTime) {
        this.endTime = endTime;
    }
    
    public CalendarEventType getEventType() {
        return eventType;
    }
    
    public void setEventType(CalendarEventType eventType) {
        this.eventType = eventType;
    }
    
    public Boolean getIsAvailable() {
        return isAvailable;
    }
    
    public void setIsAvailable(Boolean isAvailable) {
        this.isAvailable = isAvailable;
    }
    
    public String getMeetingLink() {
        return meetingLink;
    }
    
    public void setMeetingLink(String meetingLink) {
        this.meetingLink = meetingLink;
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

