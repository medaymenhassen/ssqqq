import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

def simulate_purchase_click():
    """Simulate the exact user interaction with Selenium"""
    
    print("🔍 Simulating user interaction with Selenium...")
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Uncomment the next line if you want to see the browser
    # chrome_options.add_argument("--headless")  # Run in background
    
    try:
        # Initialize the browser
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Navigate to the frontend
        print("1. Navigating to the application...")
        driver.get("http://localhost:4200")
        
        # Wait for the page to load
        time.sleep(3)
        
        # Check if we're on the home page or if we were redirected to login
        current_url = driver.current_url
        print(f"Current URL: {current_url}")
        
        if "login" in current_url.lower():
            print("⚠️ Already on login page")
        else:
            print("✅ On main page")
        
        # Try to find login button or link if we're not logged in
        try:
            login_link = driver.find_element(By.XPATH, "//a[contains(text(), 'Login')] | //button[contains(text(), 'Login')]")
            print("Found login button/link, clicking...")
            login_link.click()
            time.sleep(2)
        except:
            print("No login button found, may already be on login page or logged in")
        
        # Now try to login
        print("2. Attempting to login...")
        
        # Wait for email input field
        try:
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name='email'], input[placeholder*='email' i]"))
            )
            email_field.clear()
            email_field.send_keys("udevetyffi-0610@yopmail.com")
            print("✅ Email entered")
        except:
            print("❌ Could not find email field")
            return False
        
        # Wait for password input field
        try:
            password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password'], input[name='password'], input[placeholder*='password' i]")
            password_field.clear()
            password_field.send_keys("udevetyffi-0610@yopmail.com")
            print("✅ Password entered")
        except:
            print("❌ Could not find password field")
            return False
        
        # Find and click login button
        try:
            login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Login') or contains(text(), 'Se connecter') or @type='submit']")
            login_button.click()
            print("✅ Login button clicked")
            
            # Wait for login to process
            time.sleep(3)
            
            # Check if login was successful by looking at URL or page content
            new_url = driver.current_url
            print(f"URL after login: {new_url}")
            
            if "login" in new_url.lower() or "auth" in new_url.lower():
                print("❌ Still on login page - login may have failed")
                # Check for error messages
                try:
                    error_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'error') or contains(@class, 'alert') or contains(text(), 'error') or contains(text(), 'failed')]")
                    for error in error_elements:
                        print(f"Error message found: {error.text}")
                except:
                    print("No error messages found")
            else:
                print("✅ Login appears successful")
        except:
            print("❌ Could not find or click login button")
            return False
        
        # Wait a bit more for the page to load after login
        time.sleep(3)
        
        # Now navigate to offers page or find the "Acheter" button
        print("3. Looking for offers and 'Acheter' button...")
        
        # Try to navigate to offers page
        try:
            driver.get("http://localhost:4200/offers")
            time.sleep(3)
        except:
            print("Could not navigate to offers page")
        
        # Look for the "Acheter" button
        try:
            acheter_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Acheter') or contains(text(), 'Buy') or contains(@class, 'buy')]"))
            )
            print("✅ Found 'Acheter' button")
            
            # Check if button is enabled
            if acheter_button.is_enabled():
                print("✅ Button is enabled")
                
                # Get button attributes
                button_class = acheter_button.get_attribute("class")
                button_id = acheter_button.get_attribute("id")
                print(f"Button class: {button_class}")
                print(f"Button ID: {button_id}")
                
                # Store current URL before clicking
                url_before_click = driver.current_url
                print(f"URL before click: {url_before_click}")
                
                # Click the button
                acheter_button.click()
                print("✅ 'Acheter' button clicked")
                
                # Wait for action to complete
                time.sleep(3)
                
                # Check URL after click
                url_after_click = driver.current_url
                print(f"URL after click: {url_after_click}")
                
                if "login" in url_after_click.lower():
                    print("❌ Redirected to login after clicking 'Acheter' - this is the issue!")
                    return False
                else:
                    print("✅ Did not redirect to login after clicking 'Acheter'")
                    return True
            else:
                print("❌ Button is disabled")
                return False
                
        except Exception as e:
            print(f"❌ Could not find 'Acheter' button: {e}")
            
            # Try to find any purchase-related buttons
            try:
                buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Purchase') or contains(text(), 'Acheter') or contains(text(), 'Buy') or contains(@class, 'buy') or contains(@class, 'purchase')]")
                if buttons:
                    print(f"Found {len(buttons)} potential purchase buttons:")
                    for i, btn in enumerate(buttons):
                        print(f"  Button {i+1}: {btn.text} (class: {btn.get_attribute('class')})")
                else:
                    print("No purchase-related buttons found")
            except:
                print("Could not search for other buttons")
            
            return False
    
    except Exception as e:
        print(f"❌ Error during Selenium test: {e}")
        return False
    
    finally:
        try:
            driver.quit()
            print("Browser closed")
        except:
            pass

def check_localstorage_token():
    """Check if the token is properly stored in localStorage"""
    
    print("\n🔍 Checking localStorage token...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Navigate to the app
        driver.get("http://localhost:4200")
        
        # Execute JavaScript to check localStorage
        try:
            local_storage = driver.execute_script("return window.localStorage;")
            print("Current localStorage contents:")
            for key, value in local_storage.items():
                if 'token' in key.lower():
                    print(f"  {key}: {value[:50]}...")  # Show first 50 chars
                else:
                    print(f"  {key}: [content hidden]")
            
            # Check specifically for access token
            access_token = driver.execute_script("return localStorage.getItem('accessToken');")
            if access_token:
                print(f"\n✅ accessToken found in localStorage: {access_token[:50]}...")
            else:
                print("\n❌ No accessToken found in localStorage")
                
        except Exception as e:
            print(f"❌ Error accessing localStorage: {e}")
        
        driver.quit()
        
    except Exception as e:
        print(f"❌ Error checking localStorage: {e}")

if __name__ == "__main__":
    print("Simulating user login and 'Acheter' button click...")
    print("="*60)
    
    # Check localStorage first
    check_localstorage_token()
    
    # Then simulate the user interaction
    success = simulate_purchase_click()
    
    print("\n" + "="*60)
    if success:
        print("✅ Test completed successfully - no redirection issue found")
    else:
        print("❌ Issue reproduced - user gets redirected to login when clicking 'Acheter'")
    
    print("\nPotential causes:")
    print("1. Token not properly stored in localStorage after login")
    print("2. Authentication guard in Angular redirecting to login")
    print("3. Token expiration or invalidation")
    print("4. Missing Authorization header in purchase request")
    print("5. Frontend authentication state not updated after login")