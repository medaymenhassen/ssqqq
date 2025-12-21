package com.auth.repository;

import com.auth.model.UserModuleCompletion;
import com.auth.model.CourseModule;
import com.auth.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface UserModuleCompletionRepository extends JpaRepository<UserModuleCompletion, Long> {
    List<UserModuleCompletion> findByUserId(Long userId);
    List<UserModuleCompletion> findByCourseModuleId(Long courseModuleId);
    Optional<UserModuleCompletion> findByUserIdAndCourseModuleId(Long userId, Long courseModuleId);
    boolean existsByUserIdAndCourseModuleId(Long userId, Long courseModuleId);
}