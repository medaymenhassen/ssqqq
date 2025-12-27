import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { TestService, CourseLesson } from '../../services/test.service';
import { CommonModule } from '@angular/common';
import { DomSanitizer, SafeHtml, Title } from '@angular/platform-browser';
import { OfferService } from '../../services/offer.service';  // Added for access control
import { AuthService, User } from '../../auth.service';
import { Observable, interval, Subscription, of, throwError } from 'rxjs';
import { map, filter, timeout, retry, catchError } from 'rxjs/operators';
import { VideoComponent } from '../../video/video.component'; // Added for 3D animation

@Component({
  selector: 'app-course-lesson-detail',
  standalone: true,
  imports: [CommonModule, RouterModule, VideoComponent], // Added VideoComponent for 3D animation
  templateUrl: './course-lesson-detail.component.html',
  styleUrls: ['./course-lesson-detail.component.scss']
})
export class CourseLessonDetailComponent implements OnInit, OnDestroy {
  lesson: CourseLesson | null = null;
  loading: boolean = true;
  error: string = '';
  processedDescription: SafeHtml = '';
  processedContentDescription: SafeHtml = '';
  
  // Timer properties for tracking lesson time
  private timerSubscription: Subscription | null = null;
  private isLessonActive = false;
  remainingTime: number | null = null; // Track remaining time in minutes
  private displayTime: number | null = null; // Track time for display purposes
  private lastUpdateTime: number | null = null; // Track when we last updated from server
  
  showVideoComponent = false; // For toggling video component visibility

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private testService: TestService,
    private offerService: OfferService,  // Added for access control
    private authService: AuthService,  // Added for user ID retrieval
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
    
    // Add event listeners for visibility changes to pause/resume timer
    // Only add listeners if in browser environment
    if (typeof window !== 'undefined' && typeof document !== 'undefined') {
      document.addEventListener('visibilitychange', this.handleVisibilityChange);
      window.addEventListener('focus', this.handleWindowFocus);
      window.addEventListener('blur', this.handleWindowBlur);
    }
  }
  
  private handleVisibilityChange = (): void => {
    if (document.hidden) {
      this.pauseTimer();
    } else {
      this.resumeTimer();
    }
  }
  
  private handleWindowFocus = (): void => {
    if (this.lesson) {
      this.resumeTimer();
    }
  }
  
  private handleWindowBlur = (): void => {
    this.pauseTimer();
  }
  
  private pauseTimer(): void {
    if (this.timerSubscription) {
      this.timerSubscription.unsubscribe();
      this.timerSubscription = null;
      this.isLessonActive = false;
      console.log('Timer paused - page not visible');
    }
  }
  
  private resumeTimer(): void {
    if (this.lesson && this.remainingTime && this.remainingTime > 0) {
      // Refresh the remaining time from server when user returns
      // Use fallback approach to avoid timeout issues
      const currentUser = this.authService.getCurrentUser();
      if (currentUser && currentUser.id) {
        // Use the available user ID directly
        this.offerService.getUserRemainingTime(currentUser.id).subscribe({
          next: (timeResponse) => {
            this.remainingTime = timeResponse.remainingMinutes;
            this.displayTime = timeResponse.remainingMinutes;
            this.lastUpdateTime = Date.now();
            
            // Now start the timer with the updated time
            this.startLessonTimer();
          },
          error: (error) => {
            console.error('Error refreshing time when returning to page:', error);
            // Start timer with existing time if refresh fails
            this.startLessonTimer();
          }
        });
      } else {
        // Fallback to observable if user not available
        this.getCurrentUserId().subscribe({
          next: (userId: number) => {
            this.offerService.getUserRemainingTime(userId).subscribe({
              next: (timeResponse) => {
                this.remainingTime = timeResponse.remainingMinutes;
                this.displayTime = timeResponse.remainingMinutes;
                this.lastUpdateTime = Date.now();
                
                // Now start the timer with the updated time
                this.startLessonTimer();
              },
              error: (error) => {
                console.error('Error refreshing time when returning to page:', error);
                // Start timer with existing time if refresh fails
                this.startLessonTimer();
              }
            });
          },
          error: (error) => {
            console.error('Error getting user ID when returning to page:', error);
            // Start timer with existing time if refresh fails
            this.startLessonTimer();
          }
        });
      }
      
      console.log('Timer resumed - page visible');
    }
  }

  loadCourseLesson(id: number): void {
    // Ensure user is loaded by triggering auth check
    this.authService.checkAndLoadUser();
    
    // Check if we have a token available first
    const token = this.getToken();
    if (!token) {
      this.error = 'You must be logged in to access lessons.';
      this.loading = false;
      // Redirect to login after showing error
      setTimeout(() => {
        this.router.navigate(['/login']);
      }, 2000);
      return;
    }
    
    // Get the current user ID from the auth service
    this.getCurrentUserId().subscribe({
      next: (userId: number) => {
        console.log(`✅ Proceeding with user ID: ${userId}`);
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
              // Check remaining time to provide more specific error
              this.offerService.getUserRemainingTime(userId).subscribe({
                next: (timeResponse) => {
                  const remainingMinutes = timeResponse.remainingMinutes;
                  // Update time display
                  this.remainingTime = remainingMinutes;
                  this.displayTime = remainingMinutes;
                  this.lastUpdateTime = Date.now();
                  
                  if (remainingMinutes <= 0) {
                    this.error = 'Your access time has expired. Please purchase an offer to continue.';
                    // Redirect to offers page after showing error
                    setTimeout(() => {
                      this.router.navigate(['/offers']);
                    }, 3000);
                  } else {
                    this.error = 'You do not have access to this content. Please purchase an offer first.';
                    // Redirect to offers page after showing error
                    setTimeout(() => {
                      this.router.navigate(['/offers']);
                    }, 3000);
                  }
                  this.loading = false;
                },
                error: (timeError) => {
                  console.error('Error getting remaining time:', timeError);
                  this.error = 'You do not have access to this content. Please purchase an offer first.';
                  this.loading = false;
                  // Set default time values
                  this.remainingTime = 0;
                  this.displayTime = 0;
                  this.lastUpdateTime = Date.now();
                  // Redirect to offers page after showing error
                  setTimeout(() => {
                    this.router.navigate(['/offers']);
                  }, 3000);
                }
              });
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
      },
      error: (error: any) => {
        console.error('Error getting current user ID:', error);
        if (error.name === 'TimeoutError') {
          console.warn('Authentication timeout - checking current user directly...');
          // Fallback: try to get user directly without observable
          const currentUser = this.authService.getCurrentUser();
          if (currentUser && currentUser.id) {
            console.log(`✅ Fallback: Using user ID ${currentUser.id} directly`);
            // Retry with the direct user ID
            this.retryLoadCourseLesson(id, currentUser.id);
          } else {
            this.error = 'Authentication is taking too long. Please refresh the page or try logging in again.';
            this.loading = false;
          }
        } else {
          // Wait a bit and try again, as the user might still be loading
          setTimeout(() => {
            const currentUser = this.authService.getCurrentUser();
            if (currentUser && currentUser.id) {
              // User is now available, retry loading
              this.retryLoadCourseLesson(id, currentUser.id);
            } else {
              this.error = 'User ID not found in token. Please log in again.';
              this.loading = false;
            }
          }, 1000);
        }
      }
    });
  }

  private retryLoadCourseLesson(id: number, userId: number): void {
    console.log(`🔄 Retrying with user ID: ${userId}`);
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
          // Check remaining time to provide more specific error
          this.offerService.getUserRemainingTime(userId).subscribe({
            next: (timeResponse) => {
              const remainingMinutes = timeResponse.remainingMinutes;
              // Update time display
              this.remainingTime = remainingMinutes;
              this.displayTime = remainingMinutes;
              this.lastUpdateTime = Date.now();
              
              if (remainingMinutes <= 0) {
                this.error = 'Your access time has expired. Please purchase an offer to continue.';
                // Redirect to offers page after showing error
                setTimeout(() => {
                  this.router.navigate(['/offers']);
                }, 3000);
              } else {
                this.error = 'You do not have access to this content. Please purchase an offer first.';
                // Redirect to offers page after showing error
                setTimeout(() => {
                  this.router.navigate(['/offers']);
                }, 3000);
              }
              this.loading = false;
            },
            error: (timeError) => {
              console.error('Error getting remaining time:', timeError);
              this.error = 'You do not have access to this content. Please purchase an offer first.';
              this.loading = false;
              // Set default time values
              this.remainingTime = 0;
              this.displayTime = 0;
              this.lastUpdateTime = Date.now();
              // Redirect to offers page after showing error
              setTimeout(() => {
                this.router.navigate(['/offers']);
              }, 3000);
            }
          });
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
        
        // The token subject (sub) contains the email, not the user ID
        // So we need to get the user ID by making an API call to get the user profile
        // For now, return null to indicate that we need to get the user ID via API
        return null;
      }
    } catch (e) {
      console.error('Error decoding token:', e);
    }
    return null;
  }
  
  private getCurrentUserId(): Observable<number> {
    // First check if user is already available
    const currentUser = this.authService.getCurrentUser();
    if (currentUser && currentUser.id) {
      console.log('✅ User ID available immediately:', currentUser.id);
      return of(currentUser.id);
    }
    
    // If not, wait for the user to be loaded with extended timeout and more retries
    console.log('⏳ Waiting for user authentication...');
    return this.authService.currentUser.pipe(
      filter((user: User | null) => user !== null && user?.id !== undefined),
      map((user: User | null) => {
        if (user && user.id) {
          console.log('✅ User ID loaded:', user.id);
          return user.id;
        } else {
          throw new Error('User ID not available');
        }
      }),
      timeout(30000), // Increased timeout to 30 seconds
      retry(5), // Retry up to 5 times
      catchError((error: any) => {
        console.error('Error getting user ID:', error);
        if (error.name === 'TimeoutError') {
          // Check again if user is available after timeout
          const currentUser = this.authService.getCurrentUser();
          if (currentUser && currentUser.id) {
            console.log('✅ User ID available after timeout:', currentUser.id);
            return of(currentUser.id);
          } else {
            // Redirect to login if still not available
            console.warn('Authentication still not available, redirecting to login');
            this.router.navigate(['/login']);
            return throwError(() => new Error('Authentication timeout - user not available'));
          }
        }
        return throwError(() => error);
      })
    );
  }

  processDescriptions(): void {
    if (this.lesson) {
      this.processedDescription = this.processMarkdown(this.lesson.description);
      this.processedContentDescription = this.processMarkdown(this.lesson.contentDescription);
      // Set the page title to the lesson title
      this.titleService.setTitle(this.lesson.title || 'Cognitiex - Lesson');
        
      // Get initial remaining time
      // Use fallback approach to avoid timeout issues
      const currentUser = this.authService.getCurrentUser();
      if (currentUser && currentUser.id) {
        // Use the available user ID directly
        this.offerService.getUserRemainingTime(currentUser.id).subscribe({
          next: (timeResponse) => {
            this.remainingTime = timeResponse.remainingMinutes;
            this.displayTime = timeResponse.remainingMinutes;
            this.lastUpdateTime = Date.now();
                              
            // Start time tracking when lesson content is loaded
            this.startLessonTimer();
          },
          error: (error) => {
            console.error('Error getting initial remaining time:', error);
            // Set default time values and start timer anyway
            this.remainingTime = 0;
            this.displayTime = 0;
            this.lastUpdateTime = Date.now();
            this.startLessonTimer();
          }
        });
      } else {
        // Fallback to observable if user not available
        this.getCurrentUserId().subscribe({
          next: (userId: number) => {
            // Get initial remaining time when lesson loads
            this.offerService.getUserRemainingTime(userId).subscribe({
              next: (timeResponse) => {
                this.remainingTime = timeResponse.remainingMinutes;
                this.displayTime = timeResponse.remainingMinutes;
                this.lastUpdateTime = Date.now();
                                  
                // Start time tracking when lesson content is loaded
                this.startLessonTimer();
              },
              error: (error) => {
                console.error('Error getting initial remaining time:', error);
                // Set default time values and start timer anyway
                this.remainingTime = 0;
                this.displayTime = 0;
                this.lastUpdateTime = Date.now();
                this.startLessonTimer();
              }
            });
          },
          error: (error) => {
            console.error('Error getting user ID for initial time check:', error);
            // Set default time values and start timer anyway
            this.remainingTime = 0;
            this.displayTime = 0;
            this.lastUpdateTime = Date.now();
            this.startLessonTimer();
          }
        });
      }
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
  
  // Method to sanitize resource URLs for videos and iframes
  sanitizeResourceUrl(url: string): SafeHtml | string {
    if (!url) return '';
    return this.sanitizer.bypassSecurityTrustResourceUrl(url);
  }

  onBack(): void {
    // Removed as per requirement to focus on selected course
  }

  onEdit(): void {
    // Removed as per requirement to focus on selected course
  }
  
  private startLessonTimer(): void {
    // Stop any existing timer to prevent multiple timers
    if (this.timerSubscription) {
      this.timerSubscription.unsubscribe();
      this.timerSubscription = null;
    }
    
    // Check if user has access to the lesson before starting the timer
    // Use fallback approach to avoid timeout issues
    const currentUser = this.authService.getCurrentUser();
    if (currentUser && currentUser.id) {
      // Use the available user ID directly
      this.offerService.userHasAccess(currentUser.id).subscribe({
        next: (hasAccess: boolean) => {
          if (hasAccess) {
            // Start the timer only if the user has access
            this.isLessonActive = true;
            
            // Set up a timer that runs every second to track lesson time
            this.timerSubscription = interval(1000).subscribe(() => {
              if (this.isLessonActive && this.lesson) {
                // Update display time in real-time
                this.updateDisplayTime();
                
                // Make API call to track lesson time
                this.trackLessonTime(currentUser.id, this.lesson.id);
              }
            });
          }
        },
        error: (error: any) => {
          console.error('Error checking user access:', error);
        }
      });
    } else {
      // Fallback to observable if user not available
      this.getCurrentUserId().subscribe({
        next: (userId: number) => {
          this.offerService.userHasAccess(userId).subscribe({
            next: (hasAccess: boolean) => {
              if (hasAccess) {
                // Start the timer only if the user has access
                this.isLessonActive = true;
                
                // Set up a timer that runs every second to track lesson time
                this.timerSubscription = interval(1000).subscribe(() => {
                  if (this.isLessonActive && this.lesson) {
                    // Update display time in real-time
                    this.updateDisplayTime();
                    
                    // Make API call to track lesson time
                    this.trackLessonTime(userId, this.lesson.id);
                  }
                });
              }
            },
            error: (error: any) => {
              console.error('Error checking user access:', error);
            }
          });
        },
        error: (error: any) => {
          console.error('Error getting user ID for timer:', error);
          // Wait and try again to get user ID for the timer
          setTimeout(() => {
            const currentUser = this.authService.getCurrentUser();
            if (currentUser && currentUser.id) {
              // Start the timer with the available user ID
              this.offerService.userHasAccess(currentUser.id).subscribe({
                next: (hasAccess: boolean) => {
                  if (hasAccess) {
                    this.isLessonActive = true;
                    this.timerSubscription = interval(1000).subscribe(() => {
                      if (this.isLessonActive && this.lesson) {
                        // Update display time in real-time
                        this.updateDisplayTime();
                        
                        this.trackLessonTime(currentUser.id, this.lesson.id);
                      }
                    });
                  }
                },
                error: (accessError: any) => {
                  console.error('Error checking user access for timer:', accessError);
                }
              });
            }
          }, 1000);
        }
      });
    }
  }
  
  private updateDisplayTime(): void {
    // Update the display time in real-time if we have server time
    if (this.remainingTime !== null && this.remainingTime > 0) {
      // Calculate elapsed time since last server sync
      const now = Date.now();
      if (this.lastUpdateTime) {
        const elapsedSeconds = (now - this.lastUpdateTime) / 1000;
        const elapsedMinutes = elapsedSeconds / 60;
        
        // Update display time based on elapsed time
        this.displayTime = Math.max(0, this.remainingTime - elapsedMinutes);
      } else {
        this.displayTime = this.remainingTime;
      }
      
      // Update last update time to now for the display calculation
      this.lastUpdateTime = now;
    }
  }
  
  private trackLessonTime(userId: number, lessonId: number): void {
    // Make API call to track lesson time and deduct from user's offer
    this.offerService.trackLessonTime(userId, lessonId).subscribe({
      next: (response) => {
        // Check remaining time after tracking
        this.offerService.getUserRemainingTime(userId).subscribe({
          next: (timeResponse) => {
            const remainingMinutes = timeResponse.remainingMinutes;
            
            // Update the remaining time for display
            this.remainingTime = remainingMinutes;
            
            // Reset display time to match server time and reset last update time
            this.displayTime = remainingMinutes;
            this.lastUpdateTime = Date.now();
            
            // If remaining time is 0, stop the lesson and redirect
            if (remainingMinutes <= 0) {
              this.isLessonActive = false;
              this.error = 'Your access time has expired. Please purchase an offer to continue.';
              
              // Stop the timer subscription
              if (this.timerSubscription) {
                this.timerSubscription.unsubscribe();
              }
              
              // Optionally redirect to offers page after a delay
              setTimeout(() => {
                this.router.navigate(['/offers']);
              }, 3000); // Redirect after 3 seconds
            }
          },
          error: (timeError) => {
            console.error('Error getting remaining time:', timeError);
          }
        });
      },
      error: (error) => {
        console.error('Error tracking lesson time:', error);
        // If there's an error, we might want to stop the timer
        // or show an error message to the user
        if (this.timerSubscription) {
          this.timerSubscription.unsubscribe();
        }
        this.error = 'Error tracking lesson time. Please refresh the page.';
        // Reset display time on error
        this.displayTime = this.remainingTime;
        this.lastUpdateTime = Date.now();
      }
    });
  }
  
  formatTime(remainingMinutes: number): string {
    if (remainingMinutes <= 0) {
      return '00:00:00';
    }
    
    const hours = Math.floor(remainingMinutes / 60);
    const minutes = Math.floor(remainingMinutes % 60);
    const seconds = 0; // We'll just show minutes precision
    
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:00`;
  }
  
  // Get the formatted time for display
  getFormattedTime(): string {
    if (this.displayTime !== null && this.displayTime >= 0) {
      return this.formatTime(this.displayTime);
    } else if (this.remainingTime !== null && this.remainingTime >= 0) {
      return this.formatTime(this.remainingTime);
    }
    return '00:00:00';
  }
  
  toggleVideoComponent(): void {
    this.showVideoComponent = !this.showVideoComponent;
  }
  
  ngOnDestroy(): void {
    // Stop the timer and clean up when component is destroyed
    this.isLessonActive = false;
    if (this.timerSubscription) {
      this.timerSubscription.unsubscribe();
    }
    
    // Remove event listeners
    // Only remove listeners if in browser environment
    if (typeof window !== 'undefined' && typeof document !== 'undefined') {
      document.removeEventListener('visibilitychange', this.handleVisibilityChange);
      window.removeEventListener('focus', this.handleWindowFocus);
      window.removeEventListener('blur', this.handleWindowBlur);
    }
  }
}