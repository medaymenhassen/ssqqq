package com.auth.model;

import com.fasterxml.jackson.annotation.JsonBackReference;
import com.fasterxml.jackson.annotation.JsonManagedReference;
import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "course_lessons")
public class CourseLesson {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private String title;
    
    @Column(length = 5000000)
    private String description;
    
    @Column(name = "video_url")
    private String videoUrl;
    
    @Column(name = "animation_3d_url")
    private String animation3dUrl;
    
    @Column(name = "content_title")
    private String contentTitle;
    
    @Column(name = "content_description", length = 1000000)
    private String contentDescription;
    
    @Column(name = "display_order")
    private Integer displayOrder = 0;
    
    @Column(name = "lesson_order")
    private Integer lessonOrder = 0;
    
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    @Column(name = "is_service")
    private Boolean isService = false;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;
    
    // Constructors
    public CourseLesson() {}
    
    public CourseLesson(String title, String description) {
        this.title = title;
        this.description = description;
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
    
    public String getVideoUrl() {
        return videoUrl;
    }
    
    public void setVideoUrl(String videoUrl) {
        this.videoUrl = videoUrl;
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
    
    public String getAnimation3dUrl() {
        return animation3dUrl;
    }
    
    public void setAnimation3dUrl(String animation3dUrl) {
        this.animation3dUrl = animation3dUrl;
    }
    
    public String getContentTitle() {
        return contentTitle;
    }
    
    public void setContentTitle(String contentTitle) {
        this.contentTitle = contentTitle;
    }
    
    public String getContentDescription() {
        return contentDescription;
    }
    
    public void setContentDescription(String contentDescription) {
        this.contentDescription = contentDescription;
    }
    
    public Integer getDisplayOrder() {
        return displayOrder;
    }
    
    public void setDisplayOrder(Integer displayOrder) {
        this.displayOrder = displayOrder;
    }
    
    public Integer getLessonOrder() {
        return lessonOrder;
    }
    
    public void setLessonOrder(Integer lessonOrder) {
        this.lessonOrder = lessonOrder;
    }
    
    public Boolean getIsService() {
        return isService;
    }
    
    public void setIsService(Boolean isService) {
        this.isService = isService;
    }
    
    public User getUser() {
        return user;
    }
    
    public void setUser(User user) {
        this.user = user;
    }
}