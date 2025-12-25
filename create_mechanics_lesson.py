#!/usr/bin/env python3
"""
Script to create an example mechanics lesson for the Cognitiex platform
This script generates a sample lesson on mechanics with sample content
"""

import json
from datetime import datetime

def create_mechanics_lesson():
    """Create an example mechanics lesson with proper structure"""
    
    lesson_data = {
        "title": "Introduction to Mechanics - Motion and Forces",
        "description": """* Fundamentals of Mechanics
This lesson covers the basic principles of mechanics including motion, forces, and Newton's laws.

* Kinematics
Kinematics is the study of motion without considering the forces that cause it.

* Dynamics
Dynamics deals with the relationship between motion and the forces that cause it.""",
        "videoUrl": "https://example.com/mechanics-video.mp4",
        "animation3dUrl": "https://example.com/mechanics-animation.glb",
        "contentTitle": "Mechanics - Chapter 1: Motion Fundamentals",
        "contentDescription": """* Position, Velocity, and Acceleration
- Position: The location of an object in space
- Velocity: The rate of change of position
- Acceleration: The rate of change of velocity

* Newton's Three Laws of Motion
- **First Law**: An object at rest stays at rest and an object in motion stays in motion unless acted upon by an external force
- **Second Law**: F = ma (Force equals mass times acceleration)
- **Third Law**: For every action, there is an equal and opposite reaction

* Types of Forces
- Gravitational Force
- Normal Force
- Friction Force
- Tension Force

* Applications in Real Life
- Automotive engineering
- Construction and architecture
- Sports science
- Space exploration""",
        "displayOrder": 1,
        "lessonOrder": 1,
        "isService": False,
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat()
    }
    
    # Save as JSON file
    with open('mechanics_lesson_example.json', 'w', encoding='utf-8') as f:
        json.dump(lesson_data, f, indent=2, ensure_ascii=False)
    
    # Also create a sample in a format that could be used for API requests
    api_payload = {
        "title": lesson_data["title"],
        "description": lesson_data["description"],
        "contentDescription": lesson_data["contentDescription"],
        "videoUrl": lesson_data["videoUrl"],
        "animation3dUrl": lesson_data["animation3dUrl"],
        "contentTitle": lesson_data["contentTitle"],
        "displayOrder": lesson_data["displayOrder"],
        "lessonOrder": lesson_data["lessonOrder"],
        "isService": lesson_data["isService"]
    }
    
    with open('mechanics_lesson_api_payload.json', 'w', encoding='utf-8') as f:
        json.dump(api_payload, f, indent=2, ensure_ascii=False)
    
    print("Created mechanics lesson example files:")
    print("- mechanics_lesson_example.json")
    print("- mechanics_lesson_api_payload.json")
    print("\nLesson Content Preview:")
    print(f"Title: {lesson_data['title']}")
    print(f"Description: {lesson_data['description'][:100]}...")
    print(f"Content Description: {lesson_data['contentDescription'][:100]}...")

def print_markdown_guide():
    """Print the markdown guide for the lesson content"""
    print("\n" + "="*60)
    print("MARKDOWN SYNTAX GUIDE FOR LESSONS")
    print("="*60)
    print("* Heading -> <h2> heading")
    print("**text** -> <strong>bold text</strong>")
    print("*text* -> <em>italic text</em>")
    print("- item -> list item in <ul><li>")
    print("Newlines -> <br> tags")
    print("Direct HTML is also supported")
    print("="*60)

if __name__ == "__main__":
    print("Creating example mechanics lesson...")
    create_mechanics_lesson()
    print_markdown_guide()