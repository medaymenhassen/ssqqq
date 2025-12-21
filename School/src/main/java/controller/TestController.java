package com.auth.controller;

import com.auth.dto.CourseTestDTO;
import com.auth.dto.TestQuestionDTO;
import com.auth.dto.TestAnswerDTO;
import com.auth.model.CourseTest;
import com.auth.model.TestQuestion;
import com.auth.model.TestAnswer;
import com.auth.service.TestService;
import org.springframework.beans.factory.annotation.Autowired;
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
    public List<TestQuestionDTO> getAllTestQuestions() {
        return testService.getAllTestQuestionsWithDTO();
    }

    @GetMapping("/questions/{id}")
    public TestQuestionDTO getTestQuestionById(@PathVariable Long id) {
        return testService.getTestQuestionDTOById(id);
    }

    @PostMapping("/questions")
    public TestQuestionDTO createTestQuestion(@RequestBody TestQuestionDTO testQuestionDTO) {
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