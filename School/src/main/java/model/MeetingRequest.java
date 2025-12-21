package com.auth.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;

@Entity
@Table(name = "meeting_requests")
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class MeetingRequest {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @NotNull
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "requester_id", nullable = false)
    @JsonIgnoreProperties({"hibernateLazyInitializer", "handler", "password"})
    private User requester; // Étudiant ou Freelance qui demande le rendez-vous
    
    @NotNull
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "company_id", nullable = false)
    @JsonIgnoreProperties({"hibernateLazyInitializer", "handler", "password"})
    private User company; // L'entreprise avec qui le rendez-vous est demandé
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "calendar_event_id")
    @JsonIgnoreProperties({"hibernateLazyInitializer", "handler", "company"})
    private CompanyCalendar calendarEvent; // L'événement de l'agenda concerné (optionnel)
    
    @NotNull
    @Column(name = "requested_start_time", nullable = false)
    private LocalDateTime requestedStartTime;
    
    @NotNull
    @Column(name = "requested_end_time", nullable = false)
    private LocalDateTime requestedEndTime;
    
    @Column(name = "status")
    @Enumerated(EnumType.STRING)
    private MeetingRequestStatus status = MeetingRequestStatus.PENDING;
    
    @Column(name = "proposed_start_time")
    private LocalDateTime proposedStartTime; // Nouvelle heure proposée par l'entreprise
    
    @Column(name = "proposed_end_time")
    private LocalDateTime proposedEndTime;
    
    @Column(name = "meeting_link")
    @Size(max = 500)
    private String meetingLink; // Lien Google Meet, Zoom, etc.
    
    @Column(name = "notes", length = 1000)
    private String notes; // Notes de l'étudiant/freelance
    
    @Column(name = "company_notes", length = 1000)
    private String companyNotes; // Notes de l'entreprise (raison du décalage, etc.)
    
    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    // Constructors
    public MeetingRequest() {}
    
    public MeetingRequest(User requester, User company, LocalDateTime requestedStartTime, LocalDateTime requestedEndTime) {
        this.requester = requester;
        this.company = company;
        this.requestedStartTime = requestedStartTime;
        this.requestedEndTime = requestedEndTime;
    }
    
    // Getters and Setters
    public Long getId() {
        return id;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public User getRequester() {
        return requester;
    }
    
    public void setRequester(User requester) {
        this.requester = requester;
    }
    
    public User getCompany() {
        return company;
    }
    
    public void setCompany(User company) {
        this.company = company;
    }
    
    public CompanyCalendar getCalendarEvent() {
        return calendarEvent;
    }
    
    public void setCalendarEvent(CompanyCalendar calendarEvent) {
        this.calendarEvent = calendarEvent;
    }
    
    public LocalDateTime getRequestedStartTime() {
        return requestedStartTime;
    }
    
    public void setRequestedStartTime(LocalDateTime requestedStartTime) {
        this.requestedStartTime = requestedStartTime;
    }
    
    public LocalDateTime getRequestedEndTime() {
        return requestedEndTime;
    }
    
    public void setRequestedEndTime(LocalDateTime requestedEndTime) {
        this.requestedEndTime = requestedEndTime;
    }
    
    public MeetingRequestStatus getStatus() {
        return status;
    }
    
    public void setStatus(MeetingRequestStatus status) {
        this.status = status;
    }
    
    public LocalDateTime getProposedStartTime() {
        return proposedStartTime;
    }
    
    public void setProposedStartTime(LocalDateTime proposedStartTime) {
        this.proposedStartTime = proposedStartTime;
    }
    
    public LocalDateTime getProposedEndTime() {
        return proposedEndTime;
    }
    
    public void setProposedEndTime(LocalDateTime proposedEndTime) {
        this.proposedEndTime = proposedEndTime;
    }
    
    public String getMeetingLink() {
        return meetingLink;
    }
    
    public void setMeetingLink(String meetingLink) {
        this.meetingLink = meetingLink;
    }
    
    public String getNotes() {
        return notes;
    }
    
    public void setNotes(String notes) {
        this.notes = notes;
    }
    
    public String getCompanyNotes() {
        return companyNotes;
    }
    
    public void setCompanyNotes(String companyNotes) {
        this.companyNotes = companyNotes;
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

