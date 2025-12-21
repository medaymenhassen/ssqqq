package com.auth.service;

import com.auth.dto.CourseLessonDTO;
import com.auth.dto.CourseTestDTO;
import com.auth.dto.TestQuestionDTO;
import com.auth.dto.TestAnswerDTO;
import com.auth.model.CourseLesson;
import com.auth.model.CourseTest;
import com.auth.model.TestQuestion;
import com.auth.model.TestAnswer;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class TestMapperService {

    // CourseTest mappings
    public CourseTestDTO toCourseTestDTO(CourseTest courseTest) {
        if (courseTest == null) {
            return null;
        }

        CourseTestDTO dto = new CourseTestDTO();
        dto.setId(courseTest.getId());
        dto.setTitle(courseTest.getTitle());
        dto.setDescription(courseTest.getDescription());
        dto.setPassingScore(courseTest.getPassingScore());
        dto.setTimeLimitMinutes(courseTest.getTimeLimitMinutes());
        dto.setCreatedAt(courseTest.getCreatedAt());
        dto.setUpdatedAt(courseTest.getUpdatedAt());
        if (courseTest.getCourse() != null) {
            dto.setCourseId(courseTest.getCourse().getId());
        }
        if (courseTest.getQuestions() != null) {
            dto.setQuestions(courseTest.getQuestions().stream()
                    .map(this::toTestQuestionDTO)
                    .collect(Collectors.toList()));
        }

        return dto;
    }

    public CourseTest toCourseTestEntity(CourseTestDTO dto) {
        if (dto == null) {
            return null;
        }

        CourseTest entity = new CourseTest();
        entity.setId(dto.getId());
        entity.setTitle(dto.getTitle());
        entity.setDescription(dto.getDescription());
        entity.setPassingScore(dto.getPassingScore());
        entity.setTimeLimitMinutes(dto.getTimeLimitMinutes());
        
        // Map questions if present
        if (dto.getQuestions() != null) {
            List<TestQuestion> questions = dto.getQuestions().stream()
                .map(this::toTestQuestionEntity)
                .peek(question -> question.setCourseTest(entity)) // Set the parent relationship
                .collect(Collectors.toList());
            entity.setQuestions(questions);
        }

        return entity;
    }

    // TestQuestion mappings
    public TestQuestionDTO toTestQuestionDTO(TestQuestion testQuestion) {
        if (testQuestion == null) {
            return null;
        }

        TestQuestionDTO dto = new TestQuestionDTO();
        dto.setId(testQuestion.getId());
        dto.setQuestionText(testQuestion.getQuestionText());
        dto.setQuestionOrder(testQuestion.getQuestionOrder());
        dto.setPoints(testQuestion.getPoints());
        if (testQuestion.getQuestionType() != null) {
            dto.setQuestionType(testQuestion.getQuestionType().name());
        }
        dto.setCreatedAt(testQuestion.getCreatedAt());
        dto.setUpdatedAt(testQuestion.getUpdatedAt());
        if (testQuestion.getCourseTest() != null) {
            dto.setCourseTestId(testQuestion.getCourseTest().getId());
        }
        if (testQuestion.getAnswers() != null) {
            dto.setAnswers(testQuestion.getAnswers().stream()
                    .map(this::toTestAnswerDTO)
                    .collect(Collectors.toList()));
        }
        
        if (testQuestion.getCourseLesson() != null) {
            dto.setCourseLessonId(testQuestion.getCourseLesson().getId());
        }

        return dto;
    }

    public TestQuestion toTestQuestionEntity(TestQuestionDTO dto) {
        if (dto == null) {
            return null;
        }

        TestQuestion entity = new TestQuestion();
        entity.setId(dto.getId());
        entity.setQuestionText(dto.getQuestionText());
        entity.setQuestionOrder(dto.getQuestionOrder());
        entity.setPoints(dto.getPoints());
        if (dto.getQuestionType() != null) {
            entity.setQuestionType(TestQuestion.QuestionType.valueOf(dto.getQuestionType()));
        }
        
        // Map answers if present
        if (dto.getAnswers() != null) {
            List<TestAnswer> answers = dto.getAnswers().stream()
                .map(this::toTestAnswerEntity)
                .peek(answer -> answer.setQuestion(entity)) // Set the parent relationship
                .collect(Collectors.toList());
            entity.setAnswers(answers);
        }
        
        // Map course lesson if present
        if (dto.getCourseLessonId() != null) {
            CourseLesson courseLesson = new CourseLesson();
            courseLesson.setId(dto.getCourseLessonId());
            entity.setCourseLesson(courseLesson);
        }

        return entity;
    }

    // TestAnswer mappings
    public TestAnswerDTO toTestAnswerDTO(TestAnswer testAnswer) {
        if (testAnswer == null) {
            return null;
        }

        TestAnswerDTO dto = new TestAnswerDTO();
        dto.setId(testAnswer.getId());
        dto.setAnswerText(testAnswer.getAnswerText());
        dto.setIsLogical(testAnswer.getIsLogical());
        dto.setIsCorrect(testAnswer.getIsCorrect());
        dto.setAnswerOrder(testAnswer.getAnswerOrder());
        dto.setCreatedAt(testAnswer.getCreatedAt());
        dto.setUpdatedAt(testAnswer.getUpdatedAt());
        if (testAnswer.getQuestion() != null) {
            dto.setQuestionId(testAnswer.getQuestion().getId());
        }

        return dto;
    }

    public TestAnswer toTestAnswerEntity(TestAnswerDTO dto) {
        if (dto == null) {
            return null;
        }

        TestAnswer entity = new TestAnswer();
        entity.setId(dto.getId());
        entity.setAnswerText(dto.getAnswerText());
        entity.setIsLogical(dto.getIsLogical());
        entity.setIsCorrect(dto.getIsCorrect());
        entity.setAnswerOrder(dto.getAnswerOrder());

        return entity;
    }
    
    // CourseLesson mappings
    public CourseLessonDTO toCourseLessonDTO(CourseLesson courseLesson) {
        if (courseLesson == null) {
            return null;
        }

        CourseLessonDTO dto = new CourseLessonDTO();
        dto.setId(courseLesson.getId());
        dto.setTitle(courseLesson.getTitle());
        dto.setDescription(courseLesson.getDescription());
        dto.setVideoUrl(courseLesson.getVideoUrl());
        dto.setAnimation3dUrl(courseLesson.getAnimation3dUrl());
        dto.setContentTitle(courseLesson.getContentTitle());
        dto.setContentDescription(courseLesson.getContentDescription());
        dto.setDisplayOrder(courseLesson.getDisplayOrder());
        dto.setLessonOrder(courseLesson.getLessonOrder());
        dto.setCreatedAt(courseLesson.getCreatedAt());
        dto.setUpdatedAt(courseLesson.getUpdatedAt());

        return dto;
    }
    
    public CourseLesson toCourseLessonEntity(CourseLessonDTO dto) {
        if (dto == null) {
            return null;
        }

        CourseLesson entity = new CourseLesson();
        entity.setId(dto.getId());
        entity.setTitle(dto.getTitle());
        entity.setDescription(dto.getDescription());
        entity.setVideoUrl(dto.getVideoUrl());
        entity.setAnimation3dUrl(dto.getAnimation3dUrl());
        entity.setContentTitle(dto.getContentTitle());
        entity.setContentDescription(dto.getContentDescription());
        entity.setDisplayOrder(dto.getDisplayOrder());
        entity.setLessonOrder(dto.getLessonOrder());

        return entity;
    }
}