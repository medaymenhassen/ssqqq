import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TestService, CourseLesson } from '../services/test.service';
import { Offer, OfferService } from '../services/offer.service';

@Component({
  selector: 'app-landing',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './landing.component.html',
  styleUrls: ['./landing.component.scss']
})
export class LandingComponent implements OnInit {
  offers: Offer[] = [];
  lessons: CourseLesson[] = [];

  constructor(private offerService: OfferService, private testService: TestService) { }

  ngOnInit(): void {
    this.loadOffers();
    this.loadLessons();
  }

  loadOffers(): void {
    // Load offers from the API
    this.offerService.getAllActiveOffers().subscribe({
      next: (offers) => {
        this.offers = offers;
      },
      error: (error) => {
        // Set to empty array if API fails
        this.offers = [];
      }
    });
  }

  loadLessons(): void {
    // Load lessons from the API
    this.testService.getAllCourseLessons().subscribe({
      next: (lessons) => {
        this.lessons = lessons;
      },
      error: (error) => {
        // Set to empty array if API fails
        this.lessons = [];
      }
    });
  }

  purchaseOffer(offerId: number): void {
    // In a real app, this would call an API to process the purchase
  }

  startLesson(lessonId: number): void {
    // In a real app, this would navigate to the lesson page
  }

  startJourney(): void {
    // In a real app, this would navigate to the onboarding or dashboard
  }
}