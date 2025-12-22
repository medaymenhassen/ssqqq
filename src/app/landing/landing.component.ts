import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { Offer, OfferService } from '../services/offer.service';
import { CourseLesson, TestService } from '../services/test.service';
import { AuthService, User } from '../auth.service';
import { LearningDashboardComponent } from '../components/learning-dashboard/learning-dashboard.component';
import { Meta, Title } from '@angular/platform-browser';

@Component({
  selector: 'app-landing',
  standalone: true,
  imports: [CommonModule, LearningDashboardComponent],
  templateUrl: './landing.component.html',
  styleUrls: ['./landing.component.scss']
})
export class LandingComponent implements OnInit {
  offers: Offer[] = [];
  lessons: CourseLesson[] = [];
  loadingOffers = false;
  loadingLessons = false;
  error: string | null = null;
  currentUser: User | null = null;

  constructor(
    private router: Router,
    private offerService: OfferService,
    private testService: TestService,
    private authService: AuthService,
    private titleService: Title,
    private metaService: Meta
  ) { }

  ngOnInit(): void {
    this.loadCurrentUser();
    this.loadOffers();
    this.loadLessons();
    
    // Set meta tags
    this.titleService.setTitle('CognitiEx — Intelligence, données et systèmes autonomes');
    
    this.metaService.addTags([
      { name: 'description', content: 'CognitiEx conçoit des systèmes capables d’analyser le comportement humain, les interactions et les contenus afin de créer des intelligences artificielles appliquées au médical, à la robotisation et aux environnements 3D.' },
      { name: 'keywords', content: 'intelligence artificielle, analyse comportementale, robotique, 3D, données, IA médicale' },
      { name: 'robots', content: 'index, follow' },
      { name: 'language', content: 'French' },
      { name: 'author', content: 'CognitiEx' },
      { property: 'og:type', content: 'website' },
      { property: 'og:url', content: 'https://cognitiex.com/' },
      { property: 'og:title', content: 'CognitiEx — Intelligence, données et systèmes autonomes' },
      { property: 'og:description', content: 'CognitiEx conçoit des systèmes capables d’analyser le comportement humain, les interactions et les contenus afin de créer des intelligences artificielles appliquées au médical, à la robotisation et aux environnements 3D.' },
      { property: 'og:image', content: '/logo.jpg' },
      { property: 'twitter:card', content: 'summary_large_image' },
      { property: 'twitter:url', content: 'https://cognitiex.com/' },
      { property: 'twitter:title', content: 'CognitiEx — Intelligence, données et systèmes autonomes' },
      { property: 'twitter:description', content: 'CognitiEx conçoit des systèmes capables d’analyser le comportement humain, les interactions et les contenus afin de créer des intelligences artificielles appliquées au médical, à la robotisation et aux environnements 3D.' },
      { property: 'twitter:image', content: '/logo.jpg' }
    ]);
  }

  loadCurrentUser(): void {
    this.currentUser = this.authService.getCurrentUser();
  }

  loadOffers(): void {
    this.loadingOffers = true;
    this.error = null;
    
    this.offerService.getAllActiveOffers().subscribe({
      next: (offers) => {
        this.offers = offers.slice(0, 3); // Show only first 3 offers
        this.loadingOffers = false;
      },
      error: (err) => {
        console.error('Error loading offers:', err);
        this.error = 'Failed to load offers. Please try again later.';
        this.loadingOffers = false;
      }
    });
  }

  loadLessons(): void {
    this.loadingLessons = true;
    this.error = null;
    
    this.testService.getAllCourseLessons().subscribe({
      next: (lessons) => {
        this.lessons = lessons.slice(0, 3); // Show only first 3 lessons
        this.loadingLessons = false;
      },
      error: (err) => {
        console.error('Error loading lessons:', err);
        this.error = 'Failed to load lessons. Please try again later.';
        this.loadingLessons = false;
      }
    });
  }

  scrollToSection(sectionId: string): void {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  }

  contactUs(): void {
    // In a real application, this would open a contact form or send an email
    alert('Thank you for your interest! We will contact you soon.');
  }

  navigateToOffers(): void {
    this.router.navigate(['/offers']);
  }

  navigateToLessons(): void {
    this.router.navigate(['/course-lessons']);
  }

  navigateToLogin(): void {
    this.router.navigate(['/login']);
  }

  navigateToRegister(): void {
    this.router.navigate(['/register']);
  }

  logout(): void {
    this.authService.logout();
    this.currentUser = null;
    // Refresh the page or navigate to home
    window.location.reload();
  }

  openFacebook(): void {
    window.open('https://www.facebook.com/cognitiex', '_blank');
  }

  openLinkedIn(): void {
    window.open('https://www.linkedin.com/company/cognitiexformation/posts/?feedView=all', '_blank');
  }

  openWhatsApp(): void {
    window.open('https://wa.me/52481433', '_blank');
  }

  callPhone(): void {
    window.location.href = 'tel:52920971';
  }
}