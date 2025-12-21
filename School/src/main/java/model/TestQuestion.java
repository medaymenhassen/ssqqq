package com.auth.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "test_questions")
public class TestQuestion {
    
    public enum QuestionType {
        MCQ, OPEN_ENDED
    }
    
    public enum ExpectedAnswerType {
        OPEN_TEXT, MULTIPLE_CHOICE
    }
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "test_id", nullable = false)
    private CourseTest courseTest;
    
    @Column(nullable = false, length = 1000)
    private String questionText;
    
    @Column(name = "question_order")
    private Integer questionOrder;
    
    @Column(name = "points")
    private Integer points = 1;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "question_type", nullable = false)
    private QuestionType questionType = QuestionType.OPEN_ENDED;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "expected_answer_type")
    private ExpectedAnswerType expectedAnswerType;
    
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    @OneToMany(mappedBy = "question", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<TestAnswer> answers = new ArrayList<>();
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "lesson_id")
    private CourseLesson courseLesson;
    
    // Constructors
    public TestQuestion() {}
    
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
    
    public CourseTest getCourseTest() {
        return courseTest;
    }
    
    public void setCourseTest(CourseTest courseTest) {
        this.courseTest = courseTest;
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
    
    public QuestionType getQuestionType() {
        return questionType;
    }
    
    public void setQuestionType(QuestionType questionType) {
        this.questionType = questionType;
    }
    
    public ExpectedAnswerType getExpectedAnswerType() {
        return expectedAnswerType;
    }
    
    public void setExpectedAnswerType(ExpectedAnswerType expectedAnswerType) {
        this.expectedAnswerType = expectedAnswerType;
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
    
    public List<TestAnswer> getAnswers() {
        return answers;
    }
    
    public void setAnswers(List<TestAnswer> answers) {
        this.answers = answers;
    }
    
    public CourseLesson getCourseLesson() {
        return courseLesson;
    }
    
    public void setCourseLesson(CourseLesson courseLesson) {
        this.courseLesson = courseLesson;
    }
}