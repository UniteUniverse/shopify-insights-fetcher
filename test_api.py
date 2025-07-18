import requests
import json
import time
import sys

# Configuration
API_BASE_URL = "http://localhost:5000/api"
TEST_WEBSITES = [
    "https://gymshark.com",
    "https://allbirds.com",
    "https://memy.co.in"
]

class ShopifyInsightsAPITest:
    def __init__(self, base_url=API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_health_check(self):
        """Test the health check endpoint"""
        print("Testing health check...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
    
    def test_analyze_brand(self, website_url, include_competitors=False):
        """Test brand analysis endpoint"""
        print(f"Testing brand analysis for {website_url}...")
        try:
            payload = {
                "website_url": website_url,
                "include_competitors": include_competitors
            }
            
            response = self.session.post(
                f"{self.base_url}/analyze",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Analysis successful for {website_url}")
                print(f"   Brand ID: {data.get('brand_id')}")
                print(f"   Brand Name: {data.get('brand_data', {}).get('name')}")
                print(f"   Is Shopify: {data.get('brand_data', {}).get('is_shopify_store')}")
                if include_competitors:
                    print(f"   Competitors found: {len(data.get('competitors', []))}")
                return data
            else:
                error_data = response.json()
                print(f"❌ Analysis failed: {error_data.get('error')}")
                return None
                
        except Exception as e:
            print(f"❌ Analysis failed with exception: {e}")
            return None
    
    def test_get_brands(self):
        """Test get all brands endpoint"""
        print("Testing get all brands...")
        try:
            response = self.session.get(f"{self.base_url}/brands")
            response.raise_for_status()
            data = response.json()
            print(f"✅ Found {data.get('count', 0)} brands")
            return data
        except Exception as e:
            print(f"❌ Get brands failed: {e}")
            return None
    
    def test_get_brand_details(self, brand_id):
        """Test get brand details endpoint"""
        print(f"Testing get brand details for ID {brand_id}...")
        try:
            response = self.session.get(f"{self.base_url}/brand/{brand_id}")
            response.raise_for_status()
            data = response.json()
            print(f"✅ Brand details retrieved for ID {brand_id}")
            brand_data = data.get('data', {}).get('brand', {})
            print(f"   Name: {brand_data.get('name')}")
            print(f"   Products: {len(data.get('data', {}).get('products', []))}")
            return data
        except Exception as e:
            print(f"❌ Get brand details failed: {e}")
            return None
    
    def test_delete_brand(self, brand_id):
        """Test delete brand endpoint"""
        print(f"Testing delete brand for ID {brand_id}...")
        try:
            response = self.session.delete(f"{self.base_url}/brand/{brand_id}")
            response.raise_for_status()
            data = response.json()
            print(f"✅ Brand {brand_id} deleted successfully")
            return data
        except Exception as e:
            print(f"❌ Delete brand failed: {e}")
            return None
    
    def run_comprehensive_test(self):
        """Run a comprehensive test of all endpoints"""
        print("=" * 60)
        print("SHOPIFY INSIGHTS FETCHER - API COMPREHENSIVE TEST")
        print("=" * 60)
        
        # Test health check
        if not self.test_health_check():
            print("❌ Health check failed. Exiting.")
            return False
        
        print()
        
        # Test brand analysis
        test_website = TEST_WEBSITES[0]  # Use first test website
        analysis_result = self.test_analyze_brand(test_website, include_competitors=True)
        
        if not analysis_result:
            print("❌ Brand analysis failed. Exiting.")
            return False
        
        brand_id = analysis_result.get('brand_id')
        print()
        
        # Test get all brands
        brands_result = self.test_get_brands()
        print()
        
        # Test get brand details
        if brand_id:
            details_result = self.test_get_brand_details(brand_id)
            print()
        
        # Test delete brand (optional - uncomment to test)
        # if brand_id:
        #     delete_result = self.test_delete_brand(brand_id)
        #     print()
        
        print("=" * 60)
        print("COMPREHENSIVE TEST COMPLETED")
        print("=" * 60)
        
        return True

def main():
    """Main function to run API tests"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = API_BASE_URL
    
    tester = ShopifyInsightsAPITest(base_url)
    
    if len(sys.argv) > 2 and sys.argv[2] == "--comprehensive":
        tester.run_comprehensive_test()
    else:
        # Quick test
        print("Running quick API test...")
        tester.test_health_check()
        print("\\nFor comprehensive test, run: python test_api.py --comprehensive")

if __name__ == "__main__":
    main()