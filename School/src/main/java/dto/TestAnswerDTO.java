package com.auth.dto;

import java.time.LocalDateTime;

public class TestAnswerDTO {
    private Long id;
    private String answerText;
    private String isLogical;
    private String isCorrect;
    private Integer answerOrder;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private Long questionId;
    private Long userId;

    // Constructors
    public TestAnswerDTO() {}

    // Getters and Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getAnswerText() {
        return answerText;
    }

    public void setAnswerText(String answerText) {
        this.answerText = answerText;
    }

    public String getIsLogical() {
        return isLogical;
    }

    public void setIsLogical(String isLogical) {
        this.isLogical = isLogical;
    }

    public String getIsCorrect() {
        return isCorrect;
    }

    public void setIsCorrect(String isCorrect) {
        this.isCorrect = isCorrect;
    }

    public Integer getAnswerOrder() {
        return answerOrder;
    }

    public void setAnswerOrder(Integer answerOrder) {
        this.answerOrder = answerOrder;
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

    public Long getQuestionId() {
        return questionId;
    }

    public void setQuestionId(Long questionId) {
        this.questionId = questionId;
    }
    
    public Long getUserId() {
        return userId;
    }
    
    public void setUserId(Long userId) {
        this.userId = userId;
    }
}