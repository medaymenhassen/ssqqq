package com.auth.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "chat_conversations")
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class ChatConversation {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @NotNull
    @Column(name = "user_id", nullable = false, unique = true)
    private Long userId; // Un seul conversation par utilisateur
    
    @Column(name = "conversation", columnDefinition = "jsonb")
    @org.hibernate.annotations.JdbcTypeCode(org.hibernate.type.SqlTypes.JSON)
    @Convert(converter = ConversationConverter.class)
    private List<ChatMessage> conversation = new ArrayList<>();
    
    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    // Classe interne pour représenter un message
    @Embeddable
    public static class ChatMessage {
        private String role; // "client" ou "chatbot"
        private String message;
        private String timestamp;
        
        public ChatMessage() {}
        
        public ChatMessage(String role, String message) {
            this.role = role;
            this.message = message;
            this.timestamp = LocalDateTime.now().toString();
        }
        
        // Getters and Setters
        public String getRole() {
            return role;
        }
        
        public void setRole(String role) {
            this.role = role;
        }
        
        public String getMessage() {
            return message;
        }
        
        public void setMessage(String message) {
            this.message = message;
        }
        
        public String getTimestamp() {
            return timestamp;
        }
        
        public void setTimestamp(String timestamp) {
            this.timestamp = timestamp;
        }
    }
    
    // Converter pour JSONB
    @Converter
    public static class ConversationConverter implements AttributeConverter<List<ChatMessage>, String> {
        private static final com.fasterxml.jackson.databind.ObjectMapper objectMapper = 
            new com.fasterxml.jackson.databind.ObjectMapper();
        
        @Override
        public String convertToDatabaseColumn(List<ChatMessage> attribute) {
            try {
                return objectMapper.writeValueAsString(attribute);
            } catch (Exception e) {
                throw new RuntimeException("Error converting conversation to JSON", e);
            }
        }
        
        @Override
        public List<ChatMessage> convertToEntityAttribute(String dbData) {
            try {
                if (dbData == null || dbData.isEmpty()) {
                    return new ArrayList<>();
                }
                return objectMapper.readValue(dbData, 
                    objectMapper.getTypeFactory().constructCollectionType(List.class, ChatMessage.class));
            } catch (Exception e) {
                throw new RuntimeException("Error converting JSON to conversation", e);
            }
        }
    }
    
    // Constructors
    public ChatConversation() {}
    
    public ChatConversation(Long userId) {
        this.userId = userId;
        this.conversation = new ArrayList<>();
    }
    
    // Getters and Setters
    public Long getId() {
        return id;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public Long getUserId() {
        return userId;
    }
    
    public void setUserId(Long userId) {
        this.userId = userId;
    }
    
    public List<ChatMessage> getConversation() {
        return conversation;
    }
    
    public void setConversation(List<ChatMessage> conversation) {
        this.conversation = conversation;
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
    
    // Helper methods
    public void addMessage(String role, String message) {
        if (this.conversation == null) {
            this.conversation = new ArrayList<>();
        }
        this.conversation.add(new ChatMessage(role, message));
    }
    
    public void addClientMessage(String message) {
        addMessage("client", message);
    }
    
    public void addChatbotMessage(String message) {
        addMessage("chatbot", message);
    }
}

