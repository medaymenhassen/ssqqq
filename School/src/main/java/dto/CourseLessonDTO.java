package com.auth.dto;

import java.time.LocalDateTime;

public class CourseLessonDTO {
    private Long id;
    private String title;
    private String description;
    private String videoUrl;
    private String animation3dUrl;
    private String contentTitle;
    private String contentDescription;
    private Integer displayOrder;
    private Integer lessonOrder;
    private Boolean isService;
    private Long userId;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    // Constructors
    public CourseLessonDTO() {}

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
    
    public Boolean getIsService() {
        return isService;
    }
    
    public void setIsService(Boolean isService) {
        this.isService = isService;
    }
    
    public Long getUserId() {
        return userId;
    }
    
    public void setUserId(Long userId) {
        this.userId = userId;
    }
}