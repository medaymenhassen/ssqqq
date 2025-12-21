package com.auth.repository;

import com.auth.model.Document;
import com.auth.model.User;
import com.auth.model.UserType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface DocumentRepository extends JpaRepository<Document, Long> {
    List<Document> findByUserId(Long userId);
    List<Document> findByUserTypeId(Long userTypeId);
    List<Document> findByUserAndUserType(User user, UserType userType);
    List<Document> findByApproved(Boolean approved);
    List<Document> findByUserIdAndApproved(Long userId, Boolean approved);
}