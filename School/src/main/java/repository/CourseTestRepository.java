package com.auth.repository;

import com.auth.model.CourseTest;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface CourseTestRepository extends JpaRepository<CourseTest, Long> {
}