#!/usr/bin/env python3
"""
Script to load database configuration from JSON file and generate Django settings
"""

import json
import os

def load_database_config():
    """Load database configuration from JSON file"""
    config_file = 'database-config.json'
    
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Database configuration file {config_file} not found")
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    return config

def generate_django_db_settings():
    """Generate Django database settings"""
    config = load_database_config()
    
    django_settings = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config['database'],
            'USER': config['user'],
            'PASSWORD': config['password'],
            'HOST': config['host'],
            'PORT': str(config['port']),
        }
    }
    
    return django_settings

def generate_spring_boot_properties():
    """Generate Spring Boot properties"""
    config = load_database_config()
    
    properties = f"""spring.datasource.url=jdbc:postgresql://{config['host']}:{config['port']}/{config['database']}
spring.datasource.username={config['user']}
spring.datasource.password={config['password']}
spring.datasource.driver-class-name={config['driver']}
spring.jpa.database-platform=org.hibernate.dialect.PostgreSQLDialect
"""
    
    return properties

if __name__ == "__main__":
    print("Database Configuration Loader")
    print("=" * 30)
    
    try:
        config = load_database_config()
        print("Loaded configuration:")
        for key, value in config.items():
            print(f"  {key}: {value}")
            
        print("\nDjango Settings:")
        django_settings = generate_django_db_settings()
        print(django_settings)
        
        print("\nSpring Boot Properties:")
        spring_properties = generate_spring_boot_properties()
        print(spring_properties)
        
    except Exception as e:
        print(f"Error: {e}")