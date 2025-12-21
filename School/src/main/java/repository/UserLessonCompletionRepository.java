package com.auth.repository;

import com.auth.model.UserLessonCompletion;
import com.auth.model.CourseLesson;
import com.auth.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface UserLessonCompletionRepository extends JpaRepository<UserLessonCompletion, Long> {
    List<UserLessonCompletion> findByUserId(Long userId);
    List<UserLessonCompletion> findByCourseLessonId(Long courseLessonId);
    Optional<UserLessonCompletion> findByUserIdAndCourseLessonId(Long userId, Long courseLessonId);
    boolean existsByUserIdAndCourseLessonId(Long userId, Long courseLessonId);
}