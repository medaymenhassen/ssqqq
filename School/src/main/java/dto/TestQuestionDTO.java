package com.auth.dto;

import java.time.LocalDateTime;
import java.util.List;

public class TestQuestionDTO {
    private Long id;
    private String questionText;
    private Integer questionOrder;
    private Integer points;
    private String questionType; // MCQ or OPEN_ENDED
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private Long courseTestId;
    private Long courseLessonId;
    private List<TestAnswerDTO> answers;

    // Constructors
    public TestQuestionDTO() {}

    // Getters and Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getQuestionText() {
        return questionText;
    }

    public void setQuestionText(String questionText) {
        this.questionText = questionText;
    }

    public Integer getQuestionOrder() {
        return questionOrder;
    }

    public void setQuestionOrder(Integer questionOrder) {
        this.questionOrder = questionOrder;
    }

    public Integer getPoints() {
        return points;
    }

    public void setPoints(Integer points) {
        this.points = points;
    }

    public String getQuestionType() {
        return questionType;
    }

    public void setQuestionType(String questionType) {
        this.questionType = questionType;
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

    public Long getCourseTestId() {
        return courseTestId;
    }

    public void setCourseTestId(Long courseTestId) {
        this.courseTestId = courseTestId;
    }

    public Long getCourseLessonId() {
        return courseLessonId;
    }
        
    public void setCourseLessonId(Long courseLessonId) {
        this.courseLessonId = courseLessonId;
    }
        
    public List<TestAnswerDTO> getAnswers() {
        return answers;
    }
        
    public void setAnswers(List<TestAnswerDTO> answers) {
        this.answers = answers;
    }
}