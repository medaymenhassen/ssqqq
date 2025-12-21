# Spring Boot Testing Guide

This guide explains how to test the Spring Boot application using the provided Python scripts.

## Prerequisites

1. Java 17 or higher
2. Maven 3.6 or higher
3. Python 3.6 or higher
4. PostgreSQL database running locally

## Setup Instructions

### 1. Database Configuration

Make sure PostgreSQL is running with the following configuration (found in `src/main/resources/application.properties`):

```
spring.datasource.url=jdbc:postgresql://localhost:5432/sss
spring.datasource.username=postgres
spring.datasource.password=mohamed0192837465MED
```

Ensure the database `sss` exists and the credentials are correct.

### 2. Running the Spring Boot Application

#### Option A: Using the batch script (Windows)
```cmd
run_springboot.bat
```

#### Option B: Manual execution
```cmd
# Clean and build the project
mvn clean package -DskipTests

# Run the application
java -jar target/School-0.0.1-SNAPSHOT.jar
```

The application will start on port 8080.

### 3. Running the Tests

#### Health Check Test
First, run the health check to verify the server is running:
```cmd
python test_server.py
```

#### Simple Workflow Test
Run a basic test that registers and logs in a user:
```cmd
python test_simple_workflow.py
```

#### Full Workflow Test
Run the complete workflow test (requires the server to be running):
```cmd
python test_full_workflow.py
```

#### Using Batch Scripts (Windows)
```cmd
# Run health check and full workflow test
run_test.bat
```

## Test Scripts Overview

1. **test_server.py** - Checks if the Spring Boot server is running and healthy
2. **test_simple_workflow.py** - Basic registration and login test
3. **test_full_workflow.py** - Complete workflow including lessons, tests, questions, and answers
4. **springboot_test.py** - Existing comprehensive test script (may need updates)

## Troubleshooting

### Common Issues

1. **Port already in use**: Make sure no other application is using port 8080
2. **Database connection failed**: Verify PostgreSQL is running and credentials are correct
3. **Missing dependencies**: Run `mvn clean package` to ensure all dependencies are downloaded
4. **Python module not found**: Install required modules with `pip install requests`

### Maven Build Issues

If you encounter Maven build errors:
```cmd
# Clean the project
mvn clean

# Update dependencies
mvn dependency:resolve

# Build again
mvn package -DskipTests
```

### Checking Application Logs

When running the Spring Boot application, watch the console output for any error messages.
Common issues include:
- Database connection problems
- Port conflicts
- Missing environment variables

## API Endpoints Tested

The test scripts verify the following endpoints:

1. **Authentication**
   - POST `/api/auth/register` - User registration
   - POST `/api/auth/login` - User login

2. **Course Lessons**
   - POST `/api/course-lessons` - Create lesson
   - GET `/api/course-lessons` - Get all lessons
   - GET `/api/course-lessons/{id}` - Get lesson by ID

3. **Course Tests**
   - POST `/api/tests/course-tests` - Create test
   - GET `/api/tests/course-tests` - Get all tests

4. **Test Questions**
   - POST `/api/tests/questions` - Create question
   - GET `/api/tests/questions` - Get all questions

5. **Test Answers**
   - POST `/api/tests/answers` - Create answer
   - GET `/api/tests/answers` - Get all answers

## Expected Results

When all tests pass successfully, you should see:
- User registered successfully
- User logged in successfully
- Lesson created with valid ID
- Test created with valid ID
- 3 questions created with valid IDs
- 9 answers created (3 for each question) with valid IDs

The test data will be stored in your PostgreSQL database.