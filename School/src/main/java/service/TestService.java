package com.auth.service;

import com.auth.dto.CourseTestDTO;
import com.auth.dto.TestQuestionDTO;
import com.auth.dto.TestAnswerDTO;
import com.auth.model.CourseTest;
import com.auth.model.TestQuestion;
import com.auth.model.TestAnswer;
import com.auth.model.User;
import com.auth.repository.CourseTestRepository;
import com.auth.repository.TestQuestionRepository;
import com.auth.repository.TestAnswerRepository;
import com.auth.repository.CourseRepository;
import com.auth.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class TestService {

    @Autowired
    private CourseTestRepository courseTestRepository;

    @Autowired
    private TestQuestionRepository testQuestionRepository;

    @Autowired
    private TestAnswerRepository testAnswerRepository;

    @Autowired
    private CourseRepository courseRepository;

    @Autowired
    private TestMapperService testMapperService;
    
    @Autowired
    private UserService userService;
    
    private User getCurrentUser() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication != null) {
            Object principal = authentication.getPrincipal();
            if (principal instanceof org.springframework.security.core.userdetails.User) {
                String username = ((org.springframework.security.core.userdetails.User) principal).getUsername();
                return userService.findByEmail(username).orElse(null);
            } else if (principal instanceof String) {
                // Sometimes the principal is just the username/email as a string
                String username = (String) principal;
                return userService.findByEmail(username).orElse(null);
            }
        }
        return null;
    }

    // CourseTest methods
    public List<CourseTest> getAllCourseTests() {
        return courseTestRepository.findAll();
    }

    public List<CourseTestDTO> getAllCourseTestsWithDTO() {
        return courseTestRepository.findAll().stream()
                .map(testMapperService::toCourseTestDTO)
                .collect(Collectors.toList());
    }

    public CourseTest getCourseTestById(Long id) {
        return courseTestRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("CourseTest not found with id: " + id));
    }

    public CourseTestDTO getCourseTestDTOById(Long id) {
        CourseTest courseTest = getCourseTestById(id);
        return testMapperService.toCourseTestDTO(courseTest);
    }

    public CourseTest createCourseTest(CourseTest courseTest) {
        return courseTestRepository.save(courseTest);
    }

    public CourseTestDTO createCourseTestFromDTO(CourseTestDTO courseTestDTO) {
        CourseTest courseTest = testMapperService.toCourseTestEntity(courseTestDTO);
        if (courseTestDTO.getCourseId() != null) {
            courseRepository.findById(courseTestDTO.getCourseId())
                    .ifPresent(courseTest::setCourse);
        }
        CourseTest savedCourseTest = courseTestRepository.save(courseTest);
        return testMapperService.toCourseTestDTO(savedCourseTest);
    }

    public CourseTest updateCourseTest(Long id, CourseTest courseTestDetails) {
        CourseTest courseTest = getCourseTestById(id);
        
        courseTest.setTitle(courseTestDetails.getTitle());
        courseTest.setDescription(courseTestDetails.getDescription());
        courseTest.setPassingScore(courseTestDetails.getPassingScore());
        courseTest.setTimeLimitMinutes(courseTestDetails.getTimeLimitMinutes());
        courseTest.setCourse(courseTestDetails.getCourse());
        
        return courseTestRepository.save(courseTest);
    }

    public CourseTestDTO updateCourseTestFromDTO(Long id, CourseTestDTO courseTestDTO) {
        CourseTest courseTest = getCourseTestById(id);
        
        courseTest.setTitle(courseTestDTO.getTitle());
        courseTest.setDescription(courseTestDTO.getDescription());
        courseTest.setPassingScore(courseTestDTO.getPassingScore());
        courseTest.setTimeLimitMinutes(courseTestDTO.getTimeLimitMinutes());
        if (courseTestDTO.getCourseId() != null) {
            courseRepository.findById(courseTestDTO.getCourseId())
                    .ifPresent(courseTest::setCourse);
        }
        
        CourseTest updatedCourseTest = courseTestRepository.save(courseTest);
        return testMapperService.toCourseTestDTO(updatedCourseTest);
    }

    public void deleteCourseTest(Long id) {
        courseTestRepository.deleteById(id);
    }

    // TestQuestion methods
    public List<TestQuestion> getAllTestQuestions() {
        return testQuestionRepository.findAll();
    }

    @Transactional(readOnly = true)
    public List<TestQuestionDTO> getAllTestQuestionsWithDTO() {
        return testQuestionRepository.findAll().stream()
                .peek(question -> {
                    // Load answers for each question
                    List<TestAnswer> answers = testAnswerRepository.findByQuestionId(question.getId());
                    question.setAnswers(answers);
                })
                .map(testMapperService::toTestQuestionDTO)
                .collect(Collectors.toList());
    }

    public List<TestQuestionDTO> getTestQuestionsByLessonIdWithDTO(Long lessonId) {
        return testQuestionRepository.findByCourseLessonId(lessonId).stream()
                .peek(question -> {
                    // Load answers for each question
                    List<TestAnswer> answers = testAnswerRepository.findByQuestionId(question.getId());
                    question.setAnswers(answers);
                })
                .map(testMapperService::toTestQuestionDTO)
                .collect(Collectors.toList());
    }

    public TestQuestion getTestQuestionById(Long id) {
        return testQuestionRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("TestQuestion not found with id: " + id));
    }

    public TestQuestionDTO getTestQuestionDTOById(Long id) {
        TestQuestion testQuestion = getTestQuestionById(id);
        // Fetch associated answers
        List<TestAnswer> answers = testAnswerRepository.findByQuestionId(id);
        testQuestion.setAnswers(answers);
        return testMapperService.toTestQuestionDTO(testQuestion);
    }

    public TestQuestion createTestQuestion(TestQuestion testQuestion) {
        return testQuestionRepository.save(testQuestion);
    }

    public TestQuestionDTO createTestQuestionFromDTO(TestQuestionDTO testQuestionDTO) {
        TestQuestion testQuestion = testMapperService.toTestQuestionEntity(testQuestionDTO);
        if (testQuestionDTO.getCourseTestId() != null) {
            courseTestRepository.findById(testQuestionDTO.getCourseTestId())
                    .ifPresent(testQuestion::setCourseTest);
        }
        // Set the current user
        User currentUser = getCurrentUser();
        if (currentUser != null) {
            testQuestion.setUser(currentUser);
        } else {
            // If no current user, throw an exception
            throw new RuntimeException("Cannot create test question without an authenticated user");
        }
        TestQuestion savedTestQuestion = testQuestionRepository.save(testQuestion);
        return testMapperService.toTestQuestionDTO(savedTestQuestion);
    }

    public TestQuestion updateTestQuestion(Long id, TestQuestion testQuestionDetails) {
        TestQuestion testQuestion = getTestQuestionById(id);
        
        testQuestion.setQuestionText(testQuestionDetails.getQuestionText());
        testQuestion.setQuestionOrder(testQuestionDetails.getQuestionOrder());
        testQuestion.setPoints(testQuestionDetails.getPoints());
        testQuestion.setQuestionType(testQuestionDetails.getQuestionType());
        testQuestion.setCourseTest(testQuestionDetails.getCourseTest());
        testQuestion.setAnswers(testQuestionDetails.getAnswers());
        
        return testQuestionRepository.save(testQuestion);
    }

    public TestQuestionDTO updateTestQuestionFromDTO(Long id, TestQuestionDTO testQuestionDTO) {
        TestQuestion testQuestion = getTestQuestionById(id);
        
        testQuestion.setQuestionText(testQuestionDTO.getQuestionText());
        testQuestion.setQuestionOrder(testQuestionDTO.getQuestionOrder());
        testQuestion.setPoints(testQuestionDTO.getPoints());
        if (testQuestionDTO.getQuestionType() != null) {
            testQuestion.setQuestionType(TestQuestion.QuestionType.valueOf(testQuestionDTO.getQuestionType()));
        }
        if (testQuestionDTO.getCourseTestId() != null) {
            courseTestRepository.findById(testQuestionDTO.getCourseTestId())
                    .ifPresent(testQuestion::setCourseTest);
        }
        // Preserve the existing user
        
        TestQuestion updatedTestQuestion = testQuestionRepository.save(testQuestion);
        return testMapperService.toTestQuestionDTO(updatedTestQuestion);
    }

    public void deleteTestQuestion(Long id) {
        testQuestionRepository.deleteById(id);
    }

    // TestAnswer methods
    public List<TestAnswer> getAllTestAnswers() {
        return testAnswerRepository.findAll();
    }

    public List<TestAnswerDTO> getAllTestAnswersWithDTO() {
        return testAnswerRepository.findAll().stream()
                .map(testMapperService::toTestAnswerDTO)
                .collect(Collectors.toList());
    }

    public TestAnswer getTestAnswerById(Long id) {
        return testAnswerRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("TestAnswer not found with id: " + id));
    }

    public TestAnswerDTO getTestAnswerDTOById(Long id) {
        TestAnswer testAnswer = getTestAnswerById(id);
        return testMapperService.toTestAnswerDTO(testAnswer);
    }

    public TestAnswer createTestAnswer(TestAnswer testAnswer) {
        return testAnswerRepository.save(testAnswer);
    }

    public TestAnswerDTO createTestAnswerFromDTO(TestAnswerDTO testAnswerDTO) {
        TestAnswer testAnswer = testMapperService.toTestAnswerEntity(testAnswerDTO);
        if (testAnswerDTO.getQuestionId() != null) {
            testQuestionRepository.findById(testAnswerDTO.getQuestionId())
                    .ifPresent(testAnswer::setQuestion);
        }
        // Set the current user
        User currentUser = getCurrentUser();
        if (currentUser != null) {
            testAnswer.setUser(currentUser);
        }
        TestAnswer savedTestAnswer = testAnswerRepository.save(testAnswer);
        return testMapperService.toTestAnswerDTO(savedTestAnswer);
    }

    public TestAnswer updateTestAnswer(Long id, TestAnswer testAnswerDetails) {
        TestAnswer testAnswer = getTestAnswerById(id);
        
        testAnswer.setAnswerText(testAnswerDetails.getAnswerText());
        testAnswer.setIsCorrect(testAnswerDetails.getIsCorrect());
        testAnswer.setAnswerOrder(testAnswerDetails.getAnswerOrder());
        testAnswer.setQuestion(testAnswerDetails.getQuestion());
        
        return testAnswerRepository.save(testAnswer);
    }

    public TestAnswerDTO updateTestAnswerFromDTO(Long id, TestAnswerDTO testAnswerDTO) {
        TestAnswer testAnswer = getTestAnswerById(id);
        
        testAnswer.setAnswerText(testAnswerDTO.getAnswerText());
        testAnswer.setIsCorrect(testAnswerDTO.getIsCorrect());
        testAnswer.setAnswerOrder(testAnswerDTO.getAnswerOrder());
        if (testAnswerDTO.getQuestionId() != null) {
            testQuestionRepository.findById(testAnswerDTO.getQuestionId())
                    .ifPresent(testAnswer::setQuestion);
        }
        // Preserve the existing user
        
        TestAnswer updatedTestAnswer = testAnswerRepository.save(testAnswer);
        return testMapperService.toTestAnswerDTO(updatedTestAnswer);
    }

    public void deleteTestAnswer(Long id) {
        testAnswerRepository.deleteById(id);
    }
}