import { Injectable } from '@angular/core';

export interface LearningObjective {
  id: string;
  title: string;
  description: string;
  category: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimatedTime: number; // in minutes
  prerequisites: string[];
  tags: string[];
}

export interface UserProgress {
  objectiveId: string;
  completed: boolean;
  progress: number; // 0-100
  lastAccessed: Date;
  timeSpent: number; // in minutes
}

@Injectable({
  providedIn: 'root'
})
export class LearningOptimizerService {
  private learningObjectives: LearningObjective[] = [
    {
      id: 'obj-001',
      title: 'Introduction aux Analyses Corporelles',
      description: 'Comprendre les bases de l\'analyse corporelle et ses applications',
      category: 'body-analysis',
      difficulty: 'beginner',
      estimatedTime: 30,
      prerequisites: [],
      tags: ['introduction', 'body-analysis', 'fundamentals']
    },
    {
      id: 'obj-002',
      title: 'Techniques d\'Analyse d\'Image Avancées',
      description: 'Maîtriser les techniques avancées d\'analyse d\'image',
      category: 'image-analysis',
      difficulty: 'intermediate',
      estimatedTime: 45,
      prerequisites: ['obj-001'],
      tags: ['image-processing', 'advanced', 'computer-vision']
    },
    {
      id: 'obj-003',
      title: 'Applications Pratiques des Bras Bioniques',
      description: 'Explorer les applications pratiques des bras bioniques dans différents domaines',
      category: 'bionics',
      difficulty: 'advanced',
      estimatedTime: 60,
      prerequisites: ['obj-002'],
      tags: ['bionics', 'applications', 'practical']
    }
  ];

  private userProgress: UserProgress[] = [];

  constructor() {
    // Initialize with sample progress data
    this.initializeSampleProgress();
  }

  private initializeSampleProgress(): void {
    this.userProgress = [
      {
        objectiveId: 'obj-001',
        completed: true,
        progress: 100,
        lastAccessed: new Date(),
        timeSpent: 35
      },
      {
        objectiveId: 'obj-002',
        completed: false,
        progress: 75,
        lastAccessed: new Date(Date.now() - 86400000), // 1 day ago
        timeSpent: 30
      }
    ];
  }

  getLearningObjectives(): LearningObjective[] {
    return this.learningObjectives;
  }

  getLearningObjectiveById(id: string): LearningObjective | undefined {
    return this.learningObjectives.find(obj => obj.id === id);
  }

  getUserProgress(): UserProgress[] {
    return this.userProgress;
  }

  getUserProgressForObjective(objectiveId: string): UserProgress | undefined {
    return this.userProgress.find(progress => progress.objectiveId === objectiveId);
  }

  updateProgress(objectiveId: string, progress: number, timeSpent: number): void {
    const existingProgress = this.userProgress.find(p => p.objectiveId === objectiveId);
    
    if (existingProgress) {
      existingProgress.progress = progress;
      existingProgress.completed = progress >= 100;
      existingProgress.lastAccessed = new Date();
      existingProgress.timeSpent += timeSpent;
    } else {
      this.userProgress.push({
        objectiveId,
        completed: progress >= 100,
        progress,
        lastAccessed: new Date(),
        timeSpent
      });
    }
  }

  getRecommendedObjectives(): LearningObjective[] {
    // Get objectives that haven't been started or are in progress
    const unfinishedObjectives = this.learningObjectives.filter(obj => {
      const progress = this.getUserProgressForObjective(obj.id);
      return !progress || progress.progress < 100;
    });

    // Sort by difficulty and prerequisites
    return unfinishedObjectives.sort((a, b) => {
      // First, check if prerequisites are met
      const aPrereqsMet = a.prerequisites.every(prereq => {
        const prereqProgress = this.getUserProgressForObjective(prereq);
        return prereqProgress && prereqProgress.completed;
      });
      
      const bPrereqsMet = b.prerequisites.every(prereq => {
        const prereqProgress = this.getUserProgressForObjective(prereq);
        return prereqProgress && prereqProgress.completed;
      });
      
      // Prioritize objectives with met prerequisites
      if (aPrereqsMet && !bPrereqsMet) return -1;
      if (!aPrereqsMet && bPrereqsMet) return 1;
      
      // Then sort by difficulty
      const difficultyOrder = { beginner: 1, intermediate: 2, advanced: 3 };
      return difficultyOrder[a.difficulty] - difficultyOrder[b.difficulty];
    });
  }

  getProgressSummary(): { total: number; completed: number; inProgress: number } {
    const total = this.learningObjectives.length;
    const completed = this.userProgress.filter(p => p.completed).length;
    const inProgress = this.userProgress.filter(p => !p.completed && p.progress > 0).length;
    
    return { total, completed, inProgress };
  }
}