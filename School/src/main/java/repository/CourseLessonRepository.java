package com.auth.repository;

import com.auth.model.CourseLesson;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface CourseLessonRepository extends JpaRepository<CourseLesson, Long> {
    List<CourseLesson> findByUserId(Long userId);
}