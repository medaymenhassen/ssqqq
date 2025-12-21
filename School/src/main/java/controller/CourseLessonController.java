package com.auth.controller;

import com.auth.dto.CourseLessonDTO;
import com.auth.service.CourseLessonService;
import com.auth.service.OfferService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/course-lessons")
@CrossOrigin(origins = {"http://localhost:4200", "https://cognitiex.com"})
public class CourseLessonController {

    @Autowired
    private CourseLessonService courseLessonService;
    
    @Autowired
    private OfferService offerService;

    @GetMapping
    public List<CourseLessonDTO> getAllCourseLessons() {
        return courseLessonService.getAllCourseLessons();
    }

    @GetMapping("/{id}")
    public ResponseEntity<CourseLessonDTO> getCourseLessonById(@PathVariable Long id, @RequestParam(required = false) Long userId) {
        // If userId is provided, check if user has access to content
        if (userId != null) {
            boolean hasAccess = offerService.userHasAccessToContent(userId);
            if (!hasAccess) {
                return ResponseEntity.status(403).build(); // Forbidden
            }
        }
        
        return courseLessonService.getCourseLessonById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public CourseLessonDTO createCourseLesson(@RequestBody CourseLessonDTO courseLessonDTO) {
        return courseLessonService.createCourseLesson(courseLessonDTO);
    }

    @PutMapping("/{id}")
    public ResponseEntity<CourseLessonDTO> updateCourseLesson(@PathVariable Long id, @RequestBody CourseLessonDTO courseLessonDTO) {
        try {
            CourseLessonDTO updatedCourseLesson = courseLessonService.updateCourseLesson(id, courseLessonDTO);
            return ResponseEntity.ok(updatedCourseLesson);
        } catch (RuntimeException e) {
            return ResponseEntity.notFound().build();
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteCourseLesson(@PathVariable Long id) {
        courseLessonService.deleteCourseLesson(id);
        return ResponseEntity.noContent().build();
    }

    @GetMapping("/user/{userId}/completed")
    public List<CourseLessonDTO> getCompletedLessonsForUser(@PathVariable Long userId) {
        return courseLessonService.getCompletedLessonsForUser(userId);
    }
    
    @GetMapping("/user/{userId}")
    public ResponseEntity<?> getLessonsForUser(@PathVariable Long userId) {
        // Check if user has access to content
        boolean hasAccess = offerService.userHasAccessToContent(userId);
        if (!hasAccess) {
            return ResponseEntity.status(403).body("Access denied. Please purchase an offer to view lessons.");
        }
        
        List<CourseLessonDTO> lessons = courseLessonService.getLessonsForUser(userId);
        return ResponseEntity.ok(lessons);
    }

    @PostMapping("/user/{userId}/lesson/{lessonId}/complete")
    public ResponseEntity<?> markLessonAsCompleted(@PathVariable Long userId, @PathVariable Long lessonId) {
        try {
            boolean isNewlyCompleted = courseLessonService.markLessonAsCompleted(userId, lessonId);
            if (isNewlyCompleted) {
                return ResponseEntity.ok().build();
            } else {
                return ResponseEntity.noContent().build();
            }
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(e.getMessage());
        }
    }
}