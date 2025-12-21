package com.auth.service;

import com.auth.dto.CourseLessonDTO;
import com.auth.model.CourseLesson;
import com.auth.repository.CourseLessonRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class CourseLessonService {

    @Autowired
    private CourseLessonRepository courseLessonRepository;

    @Autowired
    private TestMapperService testMapperService;

    public List<CourseLessonDTO> getAllCourseLessons() {
        return courseLessonRepository.findAll().stream()
                .map(testMapperService::toCourseLessonDTO)
                .collect(Collectors.toList());
    }

    public Optional<CourseLessonDTO> getCourseLessonById(Long id) {
        return courseLessonRepository.findById(id)
                .map(testMapperService::toCourseLessonDTO);
    }

    public CourseLessonDTO createCourseLesson(CourseLessonDTO courseLessonDTO) {
        CourseLesson courseLesson = testMapperService.toCourseLessonEntity(courseLessonDTO);
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

        CourseLesson updatedCourseLesson = courseLessonRepository.save(courseLesson);
        return testMapperService.toCourseLessonDTO(updatedCourseLesson);
    }

    public void deleteCourseLesson(Long id) {
        courseLessonRepository.deleteById(id);
    }
}