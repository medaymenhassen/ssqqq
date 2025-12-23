package com.auth.controller;

import com.auth.dto.CourseTestDTO;
import com.auth.dto.TestQuestionDTO;
import com.auth.dto.TestAnswerDTO;
import com.auth.model.CourseTest;
import com.auth.model.TestQuestion;
import com.auth.model.TestAnswer;
import com.auth.service.TestService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/tests")
@CrossOrigin(origins = {"http://localhost:4200", "https://cognitiex.com"})
public class TestController {

    @Autowired
    private TestService testService;

    // CourseTest endpoints
    @GetMapping("/course-tests")
    public List<CourseTestDTO> getAllCourseTests() {
        return testService.getAllCourseTestsWithDTO();
    }

    @GetMapping("/course-tests/{id}")
    public CourseTestDTO getCourseTestById(@PathVariable Long id) {
        return testService.getCourseTestDTOById(id);
    }

    @PostMapping("/course-tests")
    public CourseTestDTO createCourseTest(@RequestBody CourseTestDTO courseTestDTO) {
        return testService.createCourseTestFromDTO(courseTestDTO);
    }

    @PutMapping("/course-tests/{id}")
    public CourseTestDTO updateCourseTest(@PathVariable Long id, @RequestBody CourseTestDTO courseTestDTO) {
        return testService.updateCourseTestFromDTO(id, courseTestDTO);
    }

    @DeleteMapping("/course-tests/{id}")
    public void deleteCourseTest(@PathVariable Long id) {
        testService.deleteCourseTest(id);
    }

    // TestQuestion endpoints
    @GetMapping("/questions")
    public ResponseEntity<List<TestQuestionDTO>> getAllTestQuestions() {
        try {
            List<TestQuestionDTO> questions = testService.getAllTestQuestionsWithDTO();
            return ResponseEntity.ok(questions);
        } catch (Exception e) {
            // Log the error for debugging
            e.printStackTrace();
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    @GetMapping("/questions/lesson/{lessonId}")
    public List<TestQuestionDTO> getTestQuestionsByLessonId(@PathVariable Long lessonId) {
        return testService.getTestQuestionsByLessonIdWithDTO(lessonId);
    }

    @GetMapping("/questions/{id}")
    public TestQuestionDTO getTestQuestionById(@PathVariable Long id) {
        return testService.getTestQuestionDTOById(id);
    }

    @PostMapping("/questions")
    @PreAuthorize("hasRole('USER') or hasRole('ADMIN')")
    public TestQuestionDTO createTestQuestion(@RequestBody TestQuestionDTO testQuestionDTO) {
        System.out.println("📥 [TEST QUESTION CREATION] RECEIVED from frontend:");
        System.out.println("   Full DTO: " + testQuestionDTO);
        System.out.println("   Expected fields from TestQuestionDTO model:");
        System.out.println("   - id: Long (will be set by backend)");
        System.out.println("   - questionText: String (required)");
        System.out.println("   - questionOrder: Integer (required)");
        System.out.println("   - points: Integer (required)");
        System.out.println("   - questionType: String (required, MCQ or OPEN_ENDED)");
        System.out.println("   - createdAt: LocalDateTime (set by backend)");
        System.out.println("   - updatedAt: LocalDateTime (set by backend)");
        System.out.println("   - courseTestId: Long (foreign key to CourseTest)");
        System.out.println("   - courseLessonId: Long (foreign key to CourseLesson)");
        System.out.println("   - userId: Long (set by backend from auth)");
        System.out.println("   - answers: List<TestAnswerDTO> (optional)");
        System.out.println("\n   Received values:");
        System.out.println("   - questionText: '" + testQuestionDTO.getQuestionText() + "' (type: " + (testQuestionDTO.getQuestionText() != null ? testQuestionDTO.getQuestionText().getClass().getSimpleName() : "null") + ")");
        System.out.println("   - questionOrder: " + testQuestionDTO.getQuestionOrder() + " (type: " + (testQuestionDTO.getQuestionOrder() != null ? testQuestionDTO.getQuestionOrder().getClass().getSimpleName() : "null") + ")");
        System.out.println("   - points: " + testQuestionDTO.getPoints() + " (type: " + (testQuestionDTO.getPoints() != null ? testQuestionDTO.getPoints().getClass().getSimpleName() : "null") + ")");
        System.out.println("   - questionType: '" + testQuestionDTO.getQuestionType() + "' (type: " + (testQuestionDTO.getQuestionType() != null ? testQuestionDTO.getQuestionType().getClass().getSimpleName() : "null") + ")");
        System.out.println("   - courseTestId: " + testQuestionDTO.getCourseTestId() + " (type: " + (testQuestionDTO.getCourseTestId() != null ? testQuestionDTO.getCourseTestId().getClass().getSimpleName() : "null") + ")");
        System.out.println("   - courseLessonId: " + testQuestionDTO.getCourseLessonId() + " (type: " + (testQuestionDTO.getCourseLessonId() != null ? testQuestionDTO.getCourseLessonId().getClass().getSimpleName() : "null") + ")");
        System.out.println("   - userId: " + testQuestionDTO.getUserId() + " (should be null, set by backend)");
        
        return testService.createTestQuestionFromDTO(testQuestionDTO);
    }

    @PutMapping("/questions/{id}")
    public TestQuestionDTO updateTestQuestion(@PathVariable Long id, @RequestBody TestQuestionDTO testQuestionDTO) {
        return testService.updateTestQuestionFromDTO(id, testQuestionDTO);
    }

    @DeleteMapping("/questions/{id}")
    public void deleteTestQuestion(@PathVariable Long id) {
        testService.deleteTestQuestion(id);
    }

    // TestAnswer endpoints
    @GetMapping("/answers")
    public List<TestAnswerDTO> getAllTestAnswers() {
        return testService.getAllTestAnswersWithDTO();
    }

    @GetMapping("/answers/{id}")
    public TestAnswerDTO getTestAnswerById(@PathVariable Long id) {
        return testService.getTestAnswerDTOById(id);
    }

    @PostMapping("/answers")
    public TestAnswerDTO createTestAnswer(@RequestBody TestAnswerDTO testAnswerDTO) {
        return testService.createTestAnswerFromDTO(testAnswerDTO);
    }

    @PutMapping("/answers/{id}")
    public TestAnswerDTO updateTestAnswer(@PathVariable Long id, @RequestBody TestAnswerDTO testAnswerDTO) {
        return testService.updateTestAnswerFromDTO(id, testAnswerDTO);
    }

    @DeleteMapping("/answers/{id}")
    public void deleteTestAnswer(@PathVariable Long id) {
        testService.deleteTestAnswer(id);
    }
}