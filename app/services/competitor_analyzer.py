import logging
from typing import List, Dict, Any
from app.services.scraper import ShopifyScraperService
from app.services.llm_processor import LLMProcessorService
from app.utils.exceptions import ScrapingError

logger = logging.getLogger(__name__)

class CompetitorAnalyzerService:
    """Service for analyzing competitors"""
    
    def __init__(self):
        self.scraper = ShopifyScraperService()
        self.llm_processor = LLMProcessorService()
    
    def find_competitors(self, brand_name: str, industry: str = None) -> List[str]:
        """Find competitors using search (simplified implementation)"""
        # In a real implementation, this would use search APIs or other methods
        # For now, returning some common Shopify store examples
        
        competitors = []
        
        # Common Shopify stores for different industries
        common_stores = [
            "gymshark.com",
            "allbirds.com",
            "colourpop.com",
            "bombas.com",
            "casper.com",
            "warbyparker.com",
            "glossier.com",
            "away.com",
            "outdoor-voices.com",
            "everlane.com"
        ]
        
        # Return a subset as potential competitors
        # In reality, this would use search APIs, industry databases, etc.
        return common_stores[:3]
    
    def analyze_competitor(self, competitor_url: str) -> Dict[str, Any]:
        """Analyze a single competitor"""
        try:
            logger.info(f"Analyzing competitor: {competitor_url}")
            
            # Scrape competitor data
            competitor_data = self.scraper.scrape_store(competitor_url)
            
            if competitor_data.get('scraping_status') == 'failed':
                logger.error(f"Failed to scrape competitor {competitor_url}")
                return competitor_data
            
            # Process with LLM
            competitor_data = self.llm_processor.process_brand_context(competitor_data)
            
            # Add competitor-specific analysis
            competitor_data['competitor_analysis'] = self._analyze_competitor_strengths(competitor_data)
            
            return competitor_data
            
        except Exception as e:
            logger.error(f"Failed to analyze competitor {competitor_url}: {e}")
            return {
                'website_url': competitor_url,
                'scraping_status': 'failed',
                'scraping_errors': str(e)
            }
    
    def analyze_multiple_competitors(self, competitor_urls: List[str]) -> List[Dict[str, Any]]:
        """Analyze multiple competitors"""
        results = []
        
        for url in competitor_urls:
            try:
                competitor_data = self.analyze_competitor(url)
                results.append(competitor_data)
                
                # Add delay between requests
                import time
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Failed to analyze competitor {url}: {e}")
                results.append({
                    'website_url': url,
                    'scraping_status': 'failed',
                    'scraping_errors': str(e)
                })
        
        return results
    
    def _analyze_competitor_strengths(self, competitor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze competitor strengths and weaknesses"""
        analysis = {
            'strengths': [],
            'weaknesses': [],
            'opportunities': [],
            'threats': []
        }
        
        # Analyze product catalog
        product_catalog = competitor_data.get('product_catalog', [])
        if len(product_catalog) > 100:
            analysis['strengths'].append('Large product catalog')
        elif len(product_catalog) < 20:
            analysis['weaknesses'].append('Limited product range')
        
        # Analyze social media presence
        social_handles = competitor_data.get('social_handles', {})
        if len(social_handles) >= 3:
            analysis['strengths'].append('Strong social media presence')
        elif len(social_handles) < 2:
            analysis['weaknesses'].append('Limited social media presence')
        
        # Analyze hero products
        hero_products = competitor_data.get('hero_products', [])
        if len(hero_products) >= 3:
            analysis['strengths'].append('Good product merchandising')
        
        # Analyze FAQs
        faqs = competitor_data.get('faqs', [])
        if len(faqs) >= 5:
            analysis['strengths'].append('Comprehensive customer support')
        elif len(faqs) < 2:
            analysis['weaknesses'].append('Limited customer support information')
        
        # Analyze policies
        policies = [
            competitor_data.get('privacy_policy_text'),
            competitor_data.get('return_policy_text'),
            competitor_data.get('refund_policy_text')
        ]
        policy_count = sum(1 for policy in policies if policy)
        
        if policy_count >= 3:
            analysis['strengths'].append('Comprehensive policy documentation')
        elif policy_count < 2:
            analysis['weaknesses'].append('Incomplete policy information')
        
        return analysis
    
    def generate_competitive_report(self, brand_data: Dict[str, Any], competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive competitive analysis report"""
        try:
            report = {
                'brand_name': brand_data.get('name', ''),
                'analysis_date': None,
                'competitors_analyzed': len(competitors),
                'market_position': 'Unknown',
                'competitive_advantages': [],
                'competitive_disadvantages': [],
                'market_opportunities': [],
                'strategic_recommendations': []
            }
            
            # Get current date
            from datetime import datetime
            report['analysis_date'] = datetime.utcnow().isoformat()
            
            # Analyze market position
            brand_product_count = len(brand_data.get('product_catalog', []))
            competitor_product_counts = [len(comp.get('product_catalog', [])) for comp in competitors]
            
            if competitor_product_counts:
                avg_competitor_products = sum(competitor_product_counts) / len(competitor_product_counts)
                
                if brand_product_count > avg_competitor_products * 1.5:
                    report['market_position'] = 'Strong'
                elif brand_product_count > avg_competitor_products * 0.8:
                    report['market_position'] = 'Competitive'
                else:
                    report['market_position'] = 'Emerging'
            
            # Analyze competitive advantages
            brand_social_count = len(brand_data.get('social_handles', {}))
            competitor_social_counts = [len(comp.get('social_handles', {})) for comp in competitors]
            
            if competitor_social_counts:
                avg_competitor_social = sum(competitor_social_counts) / len(competitor_social_counts)
                
                if brand_social_count > avg_competitor_social:
                    report['competitive_advantages'].append('Strong social media presence')
                elif brand_social_count < avg_competitor_social:
                    report['competitive_disadvantages'].append('Limited social media presence')
            
            # Analyze FAQ completeness
            brand_faq_count = len(brand_data.get('faqs', []))
            competitor_faq_counts = [len(comp.get('faqs', [])) for comp in competitors]
            
            if competitor_faq_counts:
                avg_competitor_faqs = sum(competitor_faq_counts) / len(competitor_faq_counts)
                
                if brand_faq_count > avg_competitor_faqs:
                    report['competitive_advantages'].append('Comprehensive customer support')
                elif brand_faq_count < avg_competitor_faqs:
                    report['competitive_disadvantages'].append('Limited customer support information')
            
            # Generate strategic recommendations
            if report['market_position'] == 'Emerging':
                report['strategic_recommendations'].append('Expand product catalog')
                report['strategic_recommendations'].append('Increase social media presence')
            
            if 'Limited social media presence' in report['competitive_disadvantages']:
                report['strategic_recommendations'].append('Develop social media strategy')
            
            if 'Limited customer support information' in report['competitive_disadvantages']:
                report['strategic_recommendations'].append('Improve customer support documentation')
            
            # Use LLM for deeper analysis
            llm_analysis = self.llm_processor.generate_competitor_comparison(brand_data, competitors)
            if llm_analysis:
                report['llm_insights'] = llm_analysis
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate competitive report: {e}")
            return {
                'error': str(e),
                'brand_name': brand_data.get('name', ''),
                'analysis_date': None
            }