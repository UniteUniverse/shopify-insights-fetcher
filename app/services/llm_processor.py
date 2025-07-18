import openai
import json
import logging
from typing import Dict, List, Any, Optional
from app.utils.exceptions import LLMError
from config.config import Config

logger = logging.getLogger(__name__)

class LLMProcessorService:
    """Service for processing scraped data using LLM"""
    
    def __init__(self):
        if Config.OPENAI_API_KEY:
            openai.api_key = Config.OPENAI_API_KEY
        else:
            logger.warning("OpenAI API key not configured")
    
    def process_brand_context(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and structure brand context using LLM"""
        try:
            if not Config.OPENAI_API_KEY:
                logger.warning("OpenAI API key not configured, skipping LLM processing")
                return scraped_data
            
            # Prepare context for LLM
            context = self._prepare_brand_context(scraped_data)
            
            prompt = f"""
            Analyze the following brand information and provide a structured summary:
            
            Brand Data:
            {context}
            
            Please provide a JSON response with the following structure:
            {{
                "brand_summary": "Brief description of the brand",
                "key_features": ["feature1", "feature2", "feature3"],
                "target_audience": "Description of target audience",
                "unique_selling_points": ["usp1", "usp2"],
                "brand_positioning": "Brand positioning statement",
                "content_themes": ["theme1", "theme2"],
                "business_model": "Description of business model"
            }}
            
            Only return valid JSON.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a brand analyst. Analyze brand data and provide structured insights in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            
            try:
                llm_analysis = json.loads(content)
                scraped_data['llm_analysis'] = llm_analysis
                logger.info("Successfully processed brand context with LLM")
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {e}")
                scraped_data['llm_analysis'] = {"error": "Failed to parse LLM response"}
            
            return scraped_data
            
        except Exception as e:
            logger.error(f"LLM processing failed: {e}")
            scraped_data['llm_analysis'] = {"error": str(e)}
            return scraped_data
    
    def structure_faqs(self, faqs: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Structure and clean FAQ data using LLM"""
        try:
            if not Config.OPENAI_API_KEY or not faqs:
                return faqs
            
            faqs_text = "\\n".join([f"Q: {faq['question']}\\nA: {faq['answer']}" for faq in faqs])
            
            prompt = f"""
            Clean and structure the following FAQ data. Remove duplicates, improve formatting, and ensure consistency:
            
            {faqs_text}
            
            Return as JSON array with this structure:
            [
                {{
                    "question": "Clean question",
                    "answer": "Clean answer",
                    "category": "Category like 'Shipping', 'Returns', 'General', etc."
                }}
            ]
            
            Only return valid JSON array.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a content editor. Clean and structure FAQ data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content.strip()
            
            try:
                structured_faqs = json.loads(content)
                return structured_faqs
            except json.JSONDecodeError:
                logger.warning("Failed to parse structured FAQs, returning original")
                return faqs
                
        except Exception as e:
            logger.error(f"FAQ structuring failed: {e}")
            return faqs
    
    def extract_product_insights(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract insights from product catalog using LLM"""
        try:
            if not Config.OPENAI_API_KEY or not products:
                return {}
            
            # Prepare product summary
            product_summary = []
            for product in products[:20]:  # Limit to first 20 products
                summary = {
                    "title": product.get('title', ''),
                    "price": product.get('price', ''),
                    "type": product.get('product_type', ''),
                    "tags": product.get('tags', [])[:5]  # Limit tags
                }
                product_summary.append(summary)
            
            prompt = f"""
            Analyze this product catalog and provide insights:
            
            Products: {json.dumps(product_summary, indent=2)}
            
            Provide a JSON response with:
            {{
                "total_products": number,
                "price_range": {{"min": number, "max": number}},
                "main_categories": ["category1", "category2"],
                "popular_tags": ["tag1", "tag2"],
                "business_type": "Description of business type",
                "target_market": "Target market description",
                "product_diversity": "Assessment of product range"
            }}
            
            Only return valid JSON.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a product analyst. Analyze product catalogs and provide insights."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            content = response.choices[0].message.content.strip()
            
            try:
                insights = json.loads(content)
                insights['total_products'] = len(products)
                return insights
            except json.JSONDecodeError:
                logger.warning("Failed to parse product insights")
                return {"total_products": len(products)}
                
        except Exception as e:
            logger.error(f"Product insights extraction failed: {e}")
            return {"total_products": len(products)}
    
    def _prepare_brand_context(self, scraped_data: Dict[str, Any]) -> str:
        """Prepare brand context for LLM processing"""
        context_parts = []
        
        if scraped_data.get('name'):
            context_parts.append(f"Brand Name: {scraped_data['name']}")
        
        if scraped_data.get('brand_context'):
            context_parts.append(f"Brand Description: {scraped_data['brand_context']}")
        
        if scraped_data.get('hero_products'):
            products = [p.get('title', '') for p in scraped_data['hero_products']]
            context_parts.append(f"Featured Products: {', '.join(products)}")
        
        if scraped_data.get('social_handles'):
            social = ', '.join([f"{platform}: {handle}" for platform, handle in scraped_data['social_handles'].items()])
            context_parts.append(f"Social Media: {social}")
        
        if scraped_data.get('faqs'):
            faq_topics = [faq.get('question', '') for faq in scraped_data['faqs'][:5]]
            context_parts.append(f"Common Questions: {', '.join(faq_topics)}")
        
        if scraped_data.get('product_catalog'):
            product_types = list(set([p.get('product_type', '') for p in scraped_data['product_catalog'][:10] if p.get('product_type')]))
            context_parts.append(f"Product Types: {', '.join(product_types)}")
        
        return "\\n".join(context_parts)
    
    def generate_competitor_comparison(self, brand_data: Dict[str, Any], competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate competitor comparison analysis"""
        try:
            if not Config.OPENAI_API_KEY:
                return {}
            
            # Prepare comparison context
            brand_summary = {
                "name": brand_data.get('name', ''),
                "products": len(brand_data.get('product_catalog', [])),
                "social_presence": len(brand_data.get('social_handles', {}))
            }
            
            competitor_summaries = []
            for comp in competitors[:3]:  # Limit to 3 competitors
                comp_summary = {
                    "name": comp.get('name', ''),
                    "products": len(comp.get('product_catalog', [])),
                    "social_presence": len(comp.get('social_handles', {}))
                }
                competitor_summaries.append(comp_summary)
            
            prompt = f"""
            Compare this brand with its competitors:
            
            Brand: {json.dumps(brand_summary, indent=2)}
            
            Competitors: {json.dumps(competitor_summaries, indent=2)}
            
            Provide a JSON response with:
            {{
                "competitive_position": "Strong/Moderate/Weak",
                "key_advantages": ["advantage1", "advantage2"],
                "areas_for_improvement": ["area1", "area2"],
                "market_opportunities": ["opportunity1", "opportunity2"],
                "competitive_threats": ["threat1", "threat2"],
                "strategic_recommendations": ["recommendation1", "recommendation2"]
            }}
            
            Only return valid JSON.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a competitive analyst. Analyze brand positioning vs competitors."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            
            try:
                comparison = json.loads(content)
                return comparison
            except json.JSONDecodeError:
                logger.warning("Failed to parse competitor comparison")
                return {}
                
        except Exception as e:
            logger.error(f"Competitor comparison failed: {e}")
            return {}