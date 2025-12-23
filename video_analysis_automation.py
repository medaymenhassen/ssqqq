"""
Video Analysis Automation Script
This script opens Chrome, navigates to a video analysis URL, waits, and tracks the process.
"""
import time
import webbrowser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VideoAnalysisAutomator:
    def __init__(self, url="http://localhost:4200/bodyanalytics"):
        self.url = url
        self.driver = None
        self.start_time = None
        
    def setup_chrome_driver(self):
        """Setup Chrome WebDriver with options"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            
            # You might need to specify the path to chromedriver if it's not in PATH
            # service = Service("path/to/chromedriver")  # Uncomment and adjust if needed
            # self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("Chrome driver initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing Chrome driver: {e}")
            # Fallback to opening URL in default browser
            logger.info("Opening URL in default browser as fallback")
            webbrowser.open(self.url)
            return False
    
    def open_video_analysis_page(self):
        """Open the video analysis page in Chrome"""
        logger.info(f"Opening video analysis page: {self.url}")
        if self.driver:
            self.driver.get(self.url)
            self.start_time = datetime.now()
            logger.info("Page loaded successfully")
            return True
        else:
            logger.warning("Using fallback method - opening in default browser")
            webbrowser.open(self.url)
            self.start_time = datetime.now()
            return True
    
    def wait_for_analysis(self, wait_time=30):
        """Wait for the video analysis to complete"""
        logger.info(f"Waiting for {wait_time} seconds for video analysis...")
        
        if self.driver:
            try:
                # Wait for specific elements that indicate analysis is happening
                # This depends on your application's structure
                wait = WebDriverWait(self.driver, wait_time)
                
                # Look for elements like video stream, analysis indicators, etc.
                # Adjust these selectors based on your actual page elements
                try:
                    # Wait for video element to be present
                    video_element = wait.until(
                        EC.presence_of_element_located((By.TAG_NAME, "video"))
                    )
                    logger.info("Video element detected")
                except:
                    logger.info("No video element found, continuing...")
                
                # Wait for analysis status elements
                try:
                    analysis_status = wait.until(
                        EC.presence_of_element_located((By.CLASS_NAME, "analysis-section"))
                    )
                    logger.info("Analysis section detected")
                except:
                    logger.info("No analysis section found, continuing...")
                    
            except Exception as e:
                logger.warning(f"Error waiting for elements: {e}")
        
        # Wait for the specified time
        time.sleep(wait_time)
        logger.info(f"Wait completed after {wait_time} seconds")
    
    def track_analysis_process(self):
        """Track the analysis process"""
        if not self.start_time:
            self.start_time = datetime.now()
            
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        logger.info(f"Analysis tracking - Elapsed time: {elapsed_time:.2f} seconds")
        
        if self.driver:
            try:
                # Get page title and URL
                current_url = self.driver.current_url
                title = self.driver.title
                logger.info(f"Current page: {title}")
                logger.info(f"Current URL: {current_url}")
                
                # Check for specific elements that indicate analysis status
                try:
                    # Look for elements that might indicate analysis progress
                    status_elements = self.driver.find_elements(By.CLASS_NAME, "status-text")
                    for element in status_elements:
                        logger.info(f"Status: {element.text}")
                except:
                    logger.info("No status elements found")
                    
            except Exception as e:
                logger.error(f"Error tracking process: {e}")
        
        return elapsed_time
    
    def stop_analysis_and_close(self):
        """Stop the analysis and close the browser"""
        logger.info("Stopping analysis and closing browser...")
        
        if self.driver:
            try:
                # Take a screenshot before closing (optional)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = f"analysis_screenshot_{timestamp}.png"
                self.driver.save_screenshot(screenshot_path)
                logger.info(f"Screenshot saved: {screenshot_path}")
            except Exception as e:
                logger.warning(f"Could not save screenshot: {e}")
            
            self.driver.quit()
            logger.info("Browser closed successfully")
        else:
            logger.info("Browser was opened with default browser - please close manually")
    
    def run_complete_analysis(self, wait_time=30):
        """Run the complete analysis process"""
        logger.info("Starting complete video analysis automation...")
        
        # Setup and open the page
        if not self.setup_chrome_driver():
            logger.warning("Chrome driver not available, using fallback")
        
        self.open_video_analysis_page()
        
        # Wait for analysis
        self.wait_for_analysis(wait_time)
        
        # Track the process
        self.track_analysis_process()
        
        # Stop and close
        self.stop_analysis_and_close()
        
        logger.info("Video analysis automation completed")

def main():
    print("Video Analysis Automation Tool")
    print("This script will open Chrome, navigate to the video analysis page, wait, and track the process.")
    
    # Get URL from user or use default
    default_url = "http://localhost:4200/bodyanalytics"
    url = input(f"Enter the video analysis URL (default: {default_url}): ").strip()
    if not url:
        url = default_url
    
    # Get wait time from user
    try:
        wait_time = int(input("Enter wait time in seconds (default: 30): ") or "30")
    except ValueError:
        wait_time = 30
    
    # Create and run the automator
    automator = VideoAnalysisAutomator(url)
    
    print(f"\nStarting automation...")
    print(f"URL: {url}")
    print(f"Wait time: {wait_time} seconds")
    print("-" * 50)
    
    try:
        automator.run_complete_analysis(wait_time)
        print("\nAutomation completed successfully!")
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
        if automator.driver:
            automator.driver.quit()
    except Exception as e:
        print(f"\nError during automation: {e}")
        if automator.driver:
            automator.driver.quit()

if __name__ == "__main__":
    main()