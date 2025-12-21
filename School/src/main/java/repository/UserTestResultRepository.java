package com.auth.repository;

import com.auth.model.UserTestResult;
import com.auth.model.CourseTest;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface UserTestResultRepository extends JpaRepository<UserTestResult, Long> {
    List<UserTestResult> findByUserId(Long userId);
    List<UserTestResult> findByCourseTestId(Long courseTestId);
    Optional<UserTestResult> findByUserIdAndCourseTestId(Long userId, Long courseTestId);
}