import logging
from typing import Dict, Any, List
from app.services.scraper import ShopifyScraperService
from app.services.llm_processor import LLMProcessorService
from app.services.competitor_analyzer import CompetitorAnalyzerService
from app.models import db, Brand, Product, Competitor, Analysis
from app.utils.helpers import extract_domain
from app.utils.exceptions import ScrapingError
from datetime import datetime

logger = logging.getLogger(__name__)

class BrandAnalyzerService:
    """Main service for brand analysis"""
    
    def __init__(self):
        self.scraper = ShopifyScraperService()
        self.llm_processor = LLMProcessorService()
        self.competitor_analyzer = CompetitorAnalyzerService()
    
    def analyze_brand(self, website_url: str, include_competitors: bool = False) -> Dict[str, Any]:
        """Complete brand analysis"""
        try:
            logger.info(f"Starting brand analysis for {website_url}")
            
            # Check if brand already exists
            domain = extract_domain(website_url)
            existing_brand = Brand.query.filter_by(domain=domain).first()
            
            if existing_brand:
                logger.info(f"Brand {domain} already exists, updating...")
                brand = existing_brand
            else:
                brand = Brand()
            
            # Update brand status
            brand.scraping_status = 'in_progress'
            brand.website_url = website_url
            brand.domain = domain
            
            if not existing_brand:
                db.session.add(brand)
            
            db.session.commit()
            
            # Scrape brand data
            scraped_data = self.scraper.scrape_store(website_url)
            
            if scraped_data.get('scraping_status') == 'failed':
                brand.scraping_status = 'failed'
                brand.scraping_errors = scraped_data.get('scraping_errors')
                db.session.commit()
                return {'error': 'Failed to scrape brand data', 'brand_id': brand.id}
            
            # Process with LLM
            processed_data = self.llm_processor.process_brand_context(scraped_data)
            
            # Update brand with scraped data
            self._update_brand_from_scraped_data(brand, processed_data)
            
            # Save products
            if processed_data.get('product_catalog'):
                self._save_products(brand, processed_data['product_catalog'])
            
            # Update scraping status
            brand.scraping_status = 'completed'
            brand.last_scraped = datetime.utcnow()
            db.session.commit()
            
            result = {
                'brand_id': brand.id,
                'brand_data': brand.to_dict(),
                'analysis_status': 'completed'
            }
            
            # Analyze competitors if requested
            if include_competitors:
                competitors_data = self._analyze_competitors(brand)
                result['competitors'] = competitors_data
                
                # Generate competitive analysis
                competitive_report = self.competitor_analyzer.generate_competitive_report(
                    brand.to_dict(), 
                    competitors_data
                )
                result['competitive_analysis'] = competitive_report
                
                # Save competitive analysis
                self._save_analysis(brand, 'competitor_analysis', competitive_report)
            
            logger.info(f"Brand analysis completed for {website_url}")
            return result
            
        except Exception as e:
            logger.error(f"Brand analysis failed for {website_url}: {e}")
            
            # Update brand status
            if 'brand' in locals():
                brand.scraping_status = 'failed'
                brand.scraping_errors = str(e)
                db.session.commit()
                return {'error': str(e), 'brand_id': brand.id}
            
            return {'error': str(e)}
    
    def _update_brand_from_scraped_data(self, brand: Brand, data: Dict[str, Any]):
        """Update brand model with scraped data"""
        brand.name = data.get('name')
        brand.brand_context = data.get('brand_context')
        brand.contact_email = data.get('contact_email')
        brand.contact_phone = data.get('contact_phone')
        brand.social_handles = data.get('social_handles')
        brand.privacy_policy_url = data.get('privacy_policy_url')
        brand.privacy_policy_text = data.get('privacy_policy_text')
        brand.return_policy_url = data.get('return_policy_url')
        brand.return_policy_text = data.get('return_policy_text')
        brand.refund_policy_url = data.get('refund_policy_url')
        brand.refund_policy_text = data.get('refund_policy_text')
        brand.faqs = data.get('faqs')
        brand.important_links = data.get('important_links')
        brand.hero_products = data.get('hero_products')
        brand.is_shopify_store = data.get('is_shopify_store', False)
        brand.updated_at = datetime.utcnow()
    
    def _save_products(self, brand: Brand, products_data: List[Dict[str, Any]]):
        """Save products to database"""
        try:
            # Clear existing products
            Product.query.filter_by(brand_id=brand.id).delete()
            
            for product_data in products_data:
                product = Product(
                    brand_id=brand.id,
                    shopify_id=product_data.get('shopify_id'),
                    handle=product_data.get('handle'),
                    title=product_data.get('title'),
                    description=product_data.get('description'),
                    vendor=product_data.get('vendor'),
                    product_type=product_data.get('product_type'),
                    tags=product_data.get('tags'),
                    price=product_data.get('price'),
                    compare_at_price=product_data.get('compare_at_price'),
                    product_url=product_data.get('product_url'),
                    image_urls=[img.get('src') for img in product_data.get('images', [])],
                    featured_image=product_data.get('featured_image'),
                    available=product_data.get('available', True),
                    variants=product_data.get('variants')
                )
                
                db.session.add(product)
            
            db.session.commit()
            logger.info(f"Saved {len(products_data)} products for brand {brand.name}")
            
        except Exception as e:
            logger.error(f"Failed to save products: {e}")
            db.session.rollback()
    
    def _analyze_competitors(self, brand: Brand) -> List[Dict[str, Any]]:
        """Analyze competitors for the brand"""
        try:
            # Find competitors
            competitor_urls = self.competitor_analyzer.find_competitors(brand.name)
            
            # Analyze competitors
            competitors_data = []
            for url in competitor_urls:
                competitor_data = self.competitor_analyzer.analyze_competitor(url)
                
                if competitor_data.get('scraping_status') == 'completed':
                    # Save competitor to database
                    competitor = self._save_competitor(brand, competitor_data)
                    competitors_data.append(competitor.to_dict())
            
            return competitors_data
            
        except Exception as e:
            logger.error(f"Failed to analyze competitors: {e}")
            return []
    
    def _save_competitor(self, brand: Brand, competitor_data: Dict[str, Any]) -> Competitor:
        """Save competitor to database"""
        competitor = Competitor(
            brand_id=brand.id,
            name=competitor_data.get('name'),
            website_url=competitor_data.get('website_url'),
            domain=competitor_data.get('domain'),
            brand_context=competitor_data.get('brand_context'),
            contact_email=competitor_data.get('contact_email'),
            contact_phone=competitor_data.get('contact_phone'),
            social_handles=competitor_data.get('social_handles'),
            privacy_policy_url=competitor_data.get('privacy_policy_url'),
            privacy_policy_text=competitor_data.get('privacy_policy_text'),
            return_policy_url=competitor_data.get('return_policy_url'),
            return_policy_text=competitor_data.get('return_policy_text'),
            refund_policy_url=competitor_data.get('refund_policy_url'),
            refund_policy_text=competitor_data.get('refund_policy_text'),
            faqs=competitor_data.get('faqs'),
            important_links=competitor_data.get('important_links'),
            hero_products=competitor_data.get('hero_products'),
            is_shopify_store=competitor_data.get('is_shopify_store', False),
            scraping_status=competitor_data.get('scraping_status'),
            scraping_errors=competitor_data.get('scraping_errors')
        )
        
        db.session.add(competitor)
        db.session.commit()
        
        return competitor
    
    def _save_analysis(self, brand: Brand, analysis_type: str, analysis_data: Dict[str, Any]):
        """Save analysis to database"""
        analysis = Analysis(
            brand_id=brand.id,
            analysis_type=analysis_type,
            title=f"{analysis_type.replace('_', ' ').title()} for {brand.name}",
            description=f"Automated {analysis_type} analysis",
            results=analysis_data,
            analysis_status='completed'
        )
        
        db.session.add(analysis)
        db.session.commit()
    
    def get_brand_analysis(self, brand_id: int) -> Dict[str, Any]:
        """Get existing brand analysis"""
        brand = Brand.query.get_or_404(brand_id)
        
        result = {
            'brand': brand.to_dict(),
            'products': [product.to_dict() for product in brand.products],
            'competitors': [competitor.to_dict() for competitor in brand.competitors],
            'analyses': [analysis.to_dict() for analysis in brand.analyses]
        }
        
        return result
    
    def list_brands(self) -> List[Dict[str, Any]]:
        """List all brands"""
        brands = Brand.query.all()
        return [brand.to_dict() for brand in brands]
    
    def delete_brand(self, brand_id: int) -> bool:
        """Delete a brand and all associated data"""
        try:
            brand = Brand.query.get_or_404(brand_id)
            db.session.delete(brand)
            db.session.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to delete brand {brand_id}: {e}")
            db.session.rollback()
            return False