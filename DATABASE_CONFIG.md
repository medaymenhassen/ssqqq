# Centralized Database Configuration

This document describes the centralized database configuration used by both Django and Spring Boot applications.

## Configuration File

The database configuration is stored in a single JSON file at the root of the project:

**File: `database-config.json`**

```json
{
  "host": "localhost",
  "port": 5432,
  "user": "postgres",
  "password": "mohamed0192837465MED",
  "database": "sss",
  "driver": "org.postgresql.Driver"
}
```

## Applications Using This Configuration

### 1. Django (AI) Application

**File: `assistance/assistance/settings.py`**

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sss',
        'USER': 'postgres',
        'PASSWORD': 'mohamed0192837465MED',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 2. Spring Boot (API) Application

**File: `School/src/main/resources/application.properties`**

```properties
spring.datasource.url=jdbc:postgresql://localhost:5432/sss
spring.datasource.username=postgres
spring.datasource.password=mohamed0192837465MED
spring.datasource.driver-class-name=org.postgresql.Driver
spring.jpa.database-platform=org.hibernate.dialect.PostgreSQLDialect
```

## Loading Script

A Python script `load_db_config.py` is provided to load the configuration and generate settings for both applications.

## Benefits

1. **Single Source of Truth**: Database configuration is maintained in one place
2. **Easy Maintenance**: Changes only need to be made in one file
3. **Consistency**: Both applications use identical database connection parameters
4. **Version Control**: Configuration changes can be tracked in version control

## Usage Instructions

1. Ensure PostgreSQL is running on localhost:5432
2. Create the database `sss` in PostgreSQL
3. Verify the username and password are correct
4. Both Django and Spring Boot will automatically connect to the same database