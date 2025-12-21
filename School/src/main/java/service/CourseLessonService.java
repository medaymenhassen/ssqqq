package com.auth.service;

import com.auth.dto.CourseLessonDTO;
import com.auth.model.CourseLesson;
import com.auth.model.User;
import com.auth.model.UserLessonCompletion;
import com.auth.repository.CourseLessonRepository;
import com.auth.repository.UserLessonCompletionRepository;
import com.auth.repository.UserRepository;
import com.auth.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class CourseLessonService {

    @Autowired
    private CourseLessonRepository courseLessonRepository;

    @Autowired
    private UserLessonCompletionRepository userLessonCompletionRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private TestMapperService testMapperService;
    
    @Autowired
    private UserService userService;

    public List<CourseLessonDTO> getAllCourseLessons() {
        return courseLessonRepository.findAll().stream()
                .map(testMapperService::toCourseLessonDTO)
                .collect(Collectors.toList());
    }

    public Optional<CourseLessonDTO> getCourseLessonById(Long id) {
        return courseLessonRepository.findById(id)
                .map(testMapperService::toCourseLessonDTO);
    }

    private User getCurrentUser() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication != null && authentication.isAuthenticated()) {
            String email = authentication.getName();
            return userService.findByEmail(email).orElse(null);
        }
        return null;
    }
    
    public CourseLessonDTO createCourseLesson(CourseLessonDTO courseLessonDTO) {
        CourseLesson courseLesson = testMapperService.toCourseLessonEntity(courseLessonDTO);
        // Set the current user
        User currentUser = getCurrentUser();
        if (currentUser != null) {
            courseLesson.setUser(currentUser);
        }
        CourseLesson savedCourseLesson = courseLessonRepository.save(courseLesson);
        return testMapperService.toCourseLessonDTO(savedCourseLesson);
    }

    public CourseLessonDTO updateCourseLesson(Long id, CourseLessonDTO courseLessonDTO) {
        CourseLesson courseLesson = courseLessonRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("CourseLesson not found with id: " + id));

        courseLesson.setTitle(courseLessonDTO.getTitle());
        courseLesson.setDescription(courseLessonDTO.getDescription());
        courseLesson.setVideoUrl(courseLessonDTO.getVideoUrl());
        courseLesson.setAnimation3dUrl(courseLessonDTO.getAnimation3dUrl());
        courseLesson.setContentTitle(courseLessonDTO.getContentTitle());
        courseLesson.setContentDescription(courseLessonDTO.getContentDescription());
        courseLesson.setDisplayOrder(courseLessonDTO.getDisplayOrder());
        courseLesson.setLessonOrder(courseLessonDTO.getLessonOrder());
        // Preserve the existing user

        CourseLesson updatedCourseLesson = courseLessonRepository.save(courseLesson);
        return testMapperService.toCourseLessonDTO(updatedCourseLesson);
    }

    public void deleteCourseLesson(Long id) {
        courseLessonRepository.deleteById(id);
    }

    public List<CourseLessonDTO> getCompletedLessonsForUser(Long userId) {
        List<UserLessonCompletion> completions = userLessonCompletionRepository.findByUserId(userId);
        return completions.stream()
                .map(completion -> testMapperService.toCourseLessonDTO(completion.getCourseLesson()))
                .collect(Collectors.toList());
    }
    
    public List<CourseLessonDTO> getLessonsForUser(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found"));
        List<CourseLesson> lessons = courseLessonRepository.findByUserId(userId);
        return lessons.stream()
                .map(testMapperService::toCourseLessonDTO)
                .collect(Collectors.toList());
    }

    public boolean markLessonAsCompleted(Long userId, Long lessonId) {
        // Check if already completed
        if (userLessonCompletionRepository.existsByUserIdAndCourseLessonId(userId, lessonId)) {
            return false; // Already completed
        }
        
        // Fetch user and lesson
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found"));
        CourseLesson lesson = courseLessonRepository.findById(lessonId)
                .orElseThrow(() -> new RuntimeException("Lesson not found"));
        
        // Create completion record
        UserLessonCompletion completion = new UserLessonCompletion();
        completion.setUser(user);
        completion.setCourseLesson(lesson);
        completion.setCompletedAt(java.time.LocalDateTime.now());
        userLessonCompletionRepository.save(completion);
        return true;
    }
}