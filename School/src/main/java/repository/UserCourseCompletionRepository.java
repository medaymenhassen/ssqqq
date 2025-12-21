package com.auth.repository;

import com.auth.model.UserCourseCompletion;
import com.auth.model.Course;
import com.auth.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface UserCourseCompletionRepository extends JpaRepository<UserCourseCompletion, Long> {
    List<UserCourseCompletion> findByUserId(Long userId);
    List<UserCourseCompletion> findByCourseId(Long courseId);
    Optional<UserCourseCompletion> findByUserIdAndCourseId(Long userId, Long courseId);
    boolean existsByUserIdAndCourseId(Long userId, Long courseId);
}