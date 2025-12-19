package com.auth.dto;

import java.time.LocalDateTime;

public class DataRequest {
    private Long userId;
    private String imageData;
    private String videoUrl;
    private String jsonData;
    private LocalDateTime timestamp;
    private Boolean movementDetected;

    // Constructors
    public DataRequest() {}

    public DataRequest(Long userId, String imageData, String videoUrl, String jsonData, LocalDateTime timestamp, Boolean movementDetected) {
        this.userId = userId;
        this.imageData = imageData;
        this.videoUrl = videoUrl;
        this.jsonData = jsonData;
        this.timestamp = timestamp;
        this.movementDetected = movementDetected;
    }

    // Getters and setters
    public Long getUserId() {
        return userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }

    public String getImageData() {
        return imageData;
    }

    public void setImageData(String imageData) {
        this.imageData = imageData;
    }

    public String getVideoUrl() {
        return videoUrl;
    }

    public void setVideoUrl(String videoUrl) {
        this.videoUrl = videoUrl;
    }

    public String getJsonData() {
        return jsonData;
    }

    public void setJsonData(String jsonData) {
        this.jsonData = jsonData;
    }

    public LocalDateTime getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }

    public Boolean getMovementDetected() {
        return movementDetected;
    }

    public void setMovementDetected(Boolean movementDetected) {
        this.movementDetected = movementDetected;
    }
}