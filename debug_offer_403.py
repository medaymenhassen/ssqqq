"""
Script spécifique pour déboguer les erreurs 403 liées aux offres
et analyser les différences entre Angular et Java
"""
import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8080"

class Offer403Debugger:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        
    def setup_user(self):
        """Setup a test user with proper authentication"""
        print("="*70)
        print("SETTING UP TEST USER")
        print("="*70)
        
        # Register test user
        register_data = {
            "email": f"test_{int(time.time())}@example.com",
            "password": "password123",
            "confirmPassword": "password123",
            "firstname": "Test",
            "lastname": "User",
            "rgpdAccepted": True,
            "ccpaAccepted": False,
            "commercialUseConsent": True
        }
        
        try:
            register_response = self.session.post(
                f"{BASE_URL}/api/auth/register", 
                json=register_data
            )
            print(f"Registration: {register_response.status_code}")
            
            if register_response.status_code != 200:
                print(f"❌ Registration failed: {register_response.text}")
                return False
            
            # Login to get token
            login_data = {
                "email": register_data["email"],
                "password": "password123"
            }
            
            login_response = self.session.post(
                f"{BASE_URL}/api/auth/login",
                json=login_data
            )
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                self.access_token = login_result.get('accessToken')
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                print("✅ Successfully obtained access token")
                return True
            else:
                print(f"❌ Login failed: {login_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Setup error: {str(e)}")
            return False

    def test_offer_endpoints(self):
        """Test different offer endpoints to identify 403 causes"""
        print("\n" + "="*70)
        print("TESTING OFFER ENDPOINTS FOR 403 ISSUES")
        print("="*70)
        
        # Test 1: Get all offers (should work for anyone)
        print("\n1. Testing GET /api/offers (should be accessible)")
        response = self.session.get(f"{BASE_URL}/api/offers")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Success - can access offers")
        elif response.status_code == 403:
            print("   ❌ 403 Forbidden - unexpected for public endpoint")
        else:
            print(f"   ❌ Other status: {response.status_code}")
        
        # Test 2: Try to create an offer (should fail for non-admin)
        print("\n2. Testing POST /api/offers (should fail for non-admin user)")
        offer_data = {
            "title": "Test Offer",
            "description": "Test offer for debugging",
            "price": 9.99,
            "durationHours": 10,
            "isActive": True
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/offers",
            json=offer_data
        )
        print(f"   Status: {response.status_code}")
        print(f"   Data sent: {json.dumps(offer_data, indent=2)}")
        if response.status_code == 403:
            print("   ✅ Expected 403 - only admin can create offers")
        elif response.status_code == 200:
            print("   ⚠️  Unexpected 200 - non-admin created offer")
        else:
            print(f"   ❌ Other status: {response.status_code}")
        
        # Test 3: Check user access status
        print("\n3. Testing user access status")
        if self.user_id:
            response = self.session.get(
                f"{BASE_URL}/api/offers/user/{self.user_id}/access",
                headers={"Authorization": f'Bearer {self.access_token}'}
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                access_result = response.json()
                print(f"   Access status: {access_result}")
            elif response.status_code == 403:
                print("   ❌ 403 Forbidden - access check failed")
            else:
                print(f"   ❌ Other status: {response.status_code}")
        else:
            print("   Cannot test - no user ID available")

    def test_content_access_endpoints(self):
        """Test content access endpoints that might return 403"""
        print("\n" + "="*70)
        print("TESTING CONTENT ACCESS ENDPOINTS")
        print("="*70)
        
        # Test 1: Course lessons (may require offer purchase)
        print("\n1. Testing GET /api/course-lessons (may require offer)")
        response = self.session.get(f"{BASE_URL}/api/course-lessons")
        print(f"   Status: {response.status_code}")
        if response.status_code == 403:
            print("   ❌ 403 Forbidden - requires offer purchase")
            print("   💡 This is expected behavior - user needs to purchase an offer")
        elif response.status_code == 200:
            print("   ✅ 200 OK - access granted (offer already purchased or public)")
        else:
            print(f"   ❌ Other status: {response.status_code}")
        
        # Test 2: Test questions (may require offer)
        print("\n2. Testing GET /api/tests/questions (may require offer)")
        response = self.session.get(f"{BASE_URL}/api/tests/questions")
        print(f"   Status: {response.status_code}")
        if response.status_code == 403:
            print("   ❌ 403 Forbidden - requires offer purchase")
            print("   💡 This is expected behavior - user needs to purchase an offer")
        elif response.status_code == 200:
            print("   ✅ 200 OK - access granted")
        else:
            print(f"   ❌ Other status: {response.status_code}")
        
        # Test 3: Try to create a test question (should work with USER role)
        print("\n3. Testing POST /api/tests/questions (should work for USER)")
        question_data = {
            "questionText": "Test question for debugging",
            "questionOrder": 1,
            "points": 5,
            "questionType": "MCQ"
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/tests/questions",
            json=question_data
        )
        print(f"   Status: {response.status_code}")
        print(f"   Data sent: {json.dumps(question_data, indent=2)}")
        if response.status_code == 403:
            print("   ❌ 403 Forbidden - unexpected for USER role")
            print("   💡 Check if courseTest association is required")
        elif response.status_code == 200:
            print("   ✅ 200 OK - question created successfully")
        else:
            print(f"   ❌ Other status: {response.status_code}")

    def analyze_angular_vs_java_differences(self):
        """Analyze potential differences between Angular and Java expectations"""
        print("\n" + "="*70)
        print("ANALYZING ANGULAR vs JAVA DIFFERENCES")
        print("="*70)
        
        print("\nAngular sends (TypeScript interface):")
        print("export interface Offer {")
        print("  id: number;")
        print("  title: string;")
        print("  description: string;")
        print("  price: number;")
        print("  durationHours: number;")
        print("  userTypeId: number | null;")
        print("  isActive: boolean;")
        print("  createdAt: string;")
        print("  updatedAt: string;")
        print("}")
        
        print("\nJava expects (Offer model):")
        print("public class Offer {")
        print("  private Long id;")
        print("  private String title;          // ✅ matches")
        print("  private String description;    // ✅ matches") 
        print("  private Double price;          // ✅ number -> Double")
        print("  private Integer durationHours; // ✅ number -> Integer")
        print("  private Long userTypeId;       // ✅ number -> Long")
        print("  private Boolean isActive;      // ✅ boolean -> Boolean")
        print("  private LocalDateTime createdAt; // ✅ string -> LocalDateTime")
        print("  private LocalDateTime updatedAt;// ✅ string -> LocalDateTime")
        print("}")
        
        print("\n✅ COMPATIBILITY CHECK:")
        print("• Data types are compatible between Angular and Java")
        print("• Jackson handles JSON serialization/deserialization properly")
        print("• The 403 is likely due to AUTHORIZATION, not DATA FORMAT")
        
        print("\n❌ COMMON 403 CAUSES:")
        print("1. ADMIN endpoints accessed by non-admin user")
        print("2. Content access without purchased offer")
        print("3. Missing or invalid JWT token")
        print("4. Expired JWT token")
        print("5. Insufficient role permissions")

    def run_complete_analysis(self):
        """Run complete analysis"""
        if not self.setup_user():
            print("❌ Cannot proceed without user setup")
            return
        
        self.test_offer_endpoints()
        self.test_content_access_endpoints()
        self.analyze_angular_vs_java_differences()
        
        print("\n" + "="*70)
        print("FINAL RECOMMENDATIONS")
        print("="*70)
        print("1. Check user roles - ADMIN endpoints need ADMIN role")
        print("2. For content access, ensure user has purchased an offer")
        print("3. Verify JWT token is valid and not expired")
        print("4. Check Spring Security configuration in OfferController")
        print("5. Review @PreAuthorize annotations on endpoints")
        print("6. Ensure proper Content-Type: application/json headers")

def main():
    debugger = Offer403Debugger()
    debugger.run_complete_analysis()

if __name__ == "__main__":
    main()