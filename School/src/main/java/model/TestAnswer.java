package com.auth.model;

import com.fasterxml.jackson.annotation.JsonBackReference;
import com.fasterxml.jackson.annotation.JsonManagedReference;
import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "test_answers")
public class TestAnswer {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @JsonBackReference
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "question_id", nullable = false)
    private TestQuestion question;
    
    @Column(name = "answer_text", length = 1000)
    private String answerText;
    
    @Column(name = "is_logical")
    private String isLogical = "false";
    
    @Column(name = "is_correct")
    private String isCorrect = "false";
    
    @Column(name = "answer_order")
    private Integer answerOrder;
    
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;
    
    @OneToMany(mappedBy = "testAnswer", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Document> documents = new ArrayList<>();
    
    // Constructors
    public TestAnswer() {}
    
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
    
    public TestQuestion getQuestion() {
        return question;
    }
    
    public void setQuestion(TestQuestion question) {
        this.question = question;
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
    
    public List<Document> getDocuments() {
        return documents;
    }
    
    public void setDocuments(List<Document> documents) {
        this.documents = documents;
    }
    
    public User getUser() {
        return user;
    }
    
    public void setUser(User user) {
        this.user = user;
    }
}