import { Component, OnInit } from '@angular/core';
import { LearningOptimizerService, LearningObjective, UserProgress } from '../../services/learning-optimizer.service';
import { NgFor, NgIf } from '@angular/common';

@Component({
  selector: 'app-learning-dashboard',
  imports: [NgFor, NgIf],
  templateUrl: './learning-dashboard.component.html',
  styleUrls: ['./learning-dashboard.component.scss']
})
export class LearningDashboardComponent implements OnInit {
  learningObjectives: LearningObjective[] = [];
  userProgress: UserProgress[] = [];
  recommendedObjectives: LearningObjective[] = [];
  progressSummary: { total: number; completed: number; inProgress: number } = { total: 0, completed: 0, inProgress: 0 };

  constructor(private learningService: LearningOptimizerService) {}

  ngOnInit(): void {
    this.loadLearningData();
  }

  loadLearningData(): void {
    this.learningObjectives = this.learningService.getLearningObjectives();
    this.userProgress = this.learningService.getUserProgress();
    this.recommendedObjectives = this.learningService.getRecommendedObjectives();
    this.progressSummary = this.learningService.getProgressSummary();
  }

  getProgressForObjective(objectiveId: string): UserProgress | undefined {
    return this.userProgress.find(progress => progress.objectiveId === objectiveId);
  }

  getDifficultyClass(difficulty: string): string {
    return `difficulty-${difficulty}`;
  }

  getTitleCase(text: string): string {
    if (!text) return '';
    return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
  }

  formatTime(minutes: number): string {
    if (minutes < 60) {
      return `${minutes} min`;
    }
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}min` : `${hours}h`;
  }
}