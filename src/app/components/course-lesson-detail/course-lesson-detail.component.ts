import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { TestService, CourseLesson } from '../../services/test.service';
import { CommonModule, DatePipe } from '@angular/common';
import { DomSanitizer, SafeHtml, Title } from '@angular/platform-browser';
import { OfferService } from '../../services/offer.service';  // Added for access control

@Component({
  selector: 'app-course-lesson-detail',
  standalone: true,
  imports: [CommonModule, DatePipe, RouterModule],
  templateUrl: './course-lesson-detail.component.html',
  styleUrls: ['./course-lesson-detail.component.scss']
})
export class CourseLessonDetailComponent implements OnInit {
  lesson: CourseLesson | null = null;
  loading: boolean = true;
  error: string = '';
  processedDescription: SafeHtml = '';
  processedContentDescription: SafeHtml = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private testService: TestService,
    private offerService: OfferService,  // Added for access control
    private sanitizer: DomSanitizer,
    private titleService: Title
  ) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    const slug = this.route.snapshot.paramMap.get('slug');
    const idSlug = this.route.snapshot.paramMap.get('idSlug');
    
    if (id) {
      this.loadCourseLesson(+id);
    } else if (idSlug) {
      // If idSlug is provided (which is the case from the route)
      // Check if it's numeric (lesson ID) or slug
      if (!isNaN(Number(idSlug))) {
        // It's a numeric ID
        this.loadCourseLesson(+idSlug);
      } else {
        // It's a slug - we would need a method to get lesson by slug
        // For now, we'll assume it's an ID
        this.loadCourseLesson(+idSlug);
      }
    }
  }

  loadCourseLesson(id: number): void {
    // First check if user has access to content
    const token = this.getToken();
    if (!token) {
      this.error = 'You must be logged in to access lessons.';
      this.loading = false;
      return;
    }
    
    // Extract user ID from token
    const userId = this.getUserIdFromToken(token);
    if (!userId) {
      this.error = 'User ID not found in token.';
      this.loading = false;
      return;
    }
    
    // Check if user has access to content
    this.offerService.userHasAccess(userId).subscribe({
      next: (hasAccess: boolean) => {
        if (hasAccess) {
          // User has access, load the lesson
          this.testService.getCourseLessonById(id).subscribe({
            next: (lesson) => {
              this.lesson = lesson;
              this.processDescriptions();
              this.loading = false;
            },
            error: (error: any) => {
              this.error = 'Error loading course lesson';
              this.loading = false;
              console.error(error);
            }
          });
        } else {
          this.error = 'You do not have access to this content. Please purchase an offer first.';
          this.loading = false;
        }
      },
      error: (error: any) => {
        console.error('Error checking user access:', error);
        // Still try to load the lesson but with access warning
        this.testService.getCourseLessonById(id).subscribe({
          next: (lesson) => {
            this.lesson = lesson;
            this.processDescriptions();
            this.loading = false;
          },
          error: (error: any) => {
            this.error = 'Error loading course lesson';
            this.loading = false;
            console.error(error);
          }
        });
      }
    });
  }
  
  private getToken(): string | null {
    if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
      return localStorage.getItem('accessToken');
    }
    return null;
  }
  
  private getUserIdFromToken(token: string): number | null {
    try {
      const parts = token.split('.');
      if (parts.length === 3) {
        const payload = parts[1];
        const decodedPayload = atob(payload);
        const user = JSON.parse(decodedPayload);
        // Try to get user ID from different possible fields
        // Prioritize numeric IDs over email addresses
        let userId = null;
        if (user.id && !isNaN(user.id)) {
          userId = user.id;
        } else if (user.userId && !isNaN(user.userId)) {
          userId = user.userId;
        } else if (user.user_id && !isNaN(user.user_id)) {
          userId = user.user_id;
        } else if (user.sub && !isNaN(user.sub)) {
          // Only use sub if it's numeric (not an email)
          userId = user.sub;
        }
        
        return userId !== null ? +userId : null;
      }
    } catch (e) {
      console.error('Error decoding token:', e);
    }
    return null;
  }

  processDescriptions(): void {
    if (this.lesson) {
      this.processedDescription = this.processMarkdown(this.lesson.description);
      this.processedContentDescription = this.processMarkdown(this.lesson.contentDescription);
      // Set the page title to the lesson title
      this.titleService.setTitle(this.lesson.title || 'Cognitiex - Lesson');
    }
  }

  processMarkdown(text: string): SafeHtml {
    if (!text) return '';

    // Process headers: convert lines starting with * to h2
    let processedText = text.replace(/^\*\s*(.*?)$/gm, '<h2>$1</h2>');
    
    // Process other markdown-like elements
    // Bold: **text** -> <strong>text</strong>
    processedText = processedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Italic: *text* -> <em>text</em> (but not the ones already converted to h2)
    processedText = processedText.replace(/(?<!<h2>)\*(.*?)\*(?!\s*<\/h2>)/g, '<em>$1</em>');
    
    // Lists: - item -> <li>item</li> (within <ul>)
    processedText = processedText.replace(/(?:^|\n)-\s+(.*?)(?=\n|$)/g, '<ul><li>$1</li></ul>');
    
    // Replace multiple <ul><li> with a single <ul> list
    processedText = processedText.replace(/(<\/ul>\s*<ul>)/g, '');
    processedText = processedText.replace(/(<ul>)+/, '<ul>');
    processedText = processedText.replace(/(<\/ul>)+/, '</ul>');
    
    // Convert newlines to <br> tags
    processedText = processedText.replace(/\n/g, '<br>');
    
    // Process paragraphs: multiple newlines create paragraph breaks
    processedText = processedText.replace(/(<br>\s*){2,}/g, '</p><p>');
    processedText = '<p>' + processedText + '</p>';
    processedText = processedText.replace(/<p><\/p>/g, '');
    
    // Replace <p><br> or <br></p> with just <p>
    processedText = processedText.replace(/<p><br\s*\/?>|<br\s*\/?><\/p>/g, '<p>');
    
    // Allow any HTML that was written directly in the content
    // This is safe because we're using DomSanitizer with bypassSecurityTrustHtml
    return this.sanitizer.bypassSecurityTrustHtml(processedText);
  }

  onBack(): void {
    this.router.navigate(['/course-lessons']);
  }

  onEdit(): void {
    if (this.lesson) {
      this.router.navigate(['/course-lesson-form', this.lesson.id]);
    }
  }
}