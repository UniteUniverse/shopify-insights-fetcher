import requests
from bs4 import BeautifulSoup
import json
import time
import logging
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse, urlencode
from app.utils.helpers import (
    extract_domain, normalize_url, clean_text, extract_phone_numbers,
    extract_email_addresses, extract_social_handles, is_shopify_store,
    extract_important_links, truncate_text
)
from app.utils.exceptions import (
    ScrapingError, NetworkError, ParseError, RateLimitError, ShopifyDetectionError
)
from config.config import Config

logger = logging.getLogger(__name__)

class ShopifyScraperService:
    """Service for scraping Shopify stores"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': Config.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
    def scrape_store(self, website_url: str) -> Dict[str, Any]:
        """Main method to scrape a Shopify store"""
        try:
            logger.info(f"Starting scrape for {website_url}")
            
            # Normalize URL
            if not website_url.startswith(('http://', 'https://')):
                website_url = 'https://' + website_url
            
            domain = extract_domain(website_url)
            
            # Get main page content
            html_content = self._fetch_page(website_url)
            
            # Check if it's a Shopify store
            is_shopify = is_shopify_store(html_content, website_url)
            
            # Initialize result
            result = {
                'website_url': website_url,
                'domain': domain,
                'is_shopify_store': is_shopify,
                'scraping_status': 'completed',
                'scraping_errors': None
            }
            
            # Parse main page
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract basic information
            result.update(self._extract_basic_info(soup, website_url))
            
            # Extract contact information
            result.update(self._extract_contact_info(html_content, soup))
            
            # Extract social media handles
            result['social_handles'] = extract_social_handles(html_content)
            
            # Extract important links
            result['important_links'] = extract_important_links(html_content, website_url)
            
            # Extract policies
            result.update(self._extract_policies(soup, website_url))
            
            # Extract FAQs
            result['faqs'] = self._extract_faqs(soup, website_url)
            
            # Extract hero products (products on homepage)
            result['hero_products'] = self._extract_hero_products(soup, website_url)
            
            # Get product catalog if it's a Shopify store
            if is_shopify:
                try:
                    result['product_catalog'] = self._get_product_catalog(website_url)
                except Exception as e:
                    logger.warning(f"Failed to get product catalog: {e}")
                    result['product_catalog'] = []
            
            logger.info(f"Successfully scraped {website_url}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to scrape {website_url}: {e}")
            return {
                'website_url': website_url,
                'domain': domain if 'domain' in locals() else extract_domain(website_url),
                'is_shopify_store': False,
                'scraping_status': 'failed',
                'scraping_errors': str(e)
            }
    
    def _fetch_page(self, url: str, timeout: int = None) -> str:
        """Fetch a web page with error handling"""
        try:
            timeout = timeout or Config.REQUEST_TIMEOUT
            
            for attempt in range(Config.MAX_RETRIES):
                try:
                    response = self.session.get(url, timeout=timeout)
                    response.raise_for_status()
                    
                    # Check for rate limiting
                    if response.status_code == 429:
                        wait_time = int(response.headers.get('Retry-After', 60))
                        logger.warning(f"Rate limited, waiting {wait_time} seconds")
                        time.sleep(wait_time)
                        continue
                    
                    return response.text
                    
                except requests.RequestException as e:
                    if attempt == Config.MAX_RETRIES - 1:
                        raise NetworkError(f"Failed to fetch {url}: {e}")
                    
                    wait_time = Config.DELAY_BETWEEN_REQUESTS * (2 ** attempt)
                    logger.warning(f"Request failed, retrying in {wait_time} seconds")
                    time.sleep(wait_time)
            
        except requests.RequestException as e:
            raise NetworkError(f"Failed to fetch {url}: {e}")
    
    def _extract_basic_info(self, soup: BeautifulSoup, website_url: str) -> Dict[str, Any]:
        """Extract basic brand information"""
        result = {}
        
        # Extract brand name
        brand_name = None
        
        # Try to get from title
        title_tag = soup.find('title')
        if title_tag:
            brand_name = clean_text(title_tag.text)
        
        # Try to get from meta property
        for meta_tag in soup.find_all('meta', {'property': ['og:site_name', 'twitter:site']}):
            if meta_tag.get('content'):
                brand_name = clean_text(meta_tag.get('content'))
                break
        
        # Try to get from header or logo
        if not brand_name:
            header = soup.find('header')
            if header:
                logo = header.find(['img', 'h1', 'h2'], {'alt': True, 'title': True})
                if logo:
                    brand_name = clean_text(logo.get('alt') or logo.get('title') or logo.text)
        
        # Fallback to domain
        if not brand_name:
            brand_name = extract_domain(website_url).split('.')[0].title()
        
        result['name'] = brand_name
        
        # Extract brand description/context
        brand_context = ""
        
        # Try meta description
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            brand_context = clean_text(meta_desc.get('content'))
        
        # Try to find about section
        about_section = soup.find(['section', 'div'], {'class': lambda x: x and 'about' in x.lower()})
        if about_section:
            about_text = clean_text(about_section.get_text())
            if len(about_text) > len(brand_context):
                brand_context = about_text
        
        result['brand_context'] = truncate_text(brand_context, 1000)
        
        return result
    
    def _extract_contact_info(self, html_content: str, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract contact information"""
        result = {}
        
        # Extract email addresses
        emails = extract_email_addresses(html_content)
        if emails:
            # Filter out common non-contact emails
            filtered_emails = [email for email in emails if not any(
                skip in email.lower() for skip in ['no-reply', 'noreply', 'donotreply', 'example.com']
            )]
            result['contact_email'] = filtered_emails[0] if filtered_emails else emails[0]
        
        # Extract phone numbers
        phones = extract_phone_numbers(html_content)
        if phones:
            result['contact_phone'] = phones[0]
        
        return result
    
    def _extract_policies(self, soup: BeautifulSoup, website_url: str) -> Dict[str, Any]:
        """Extract policy information"""
        result = {}
        
        policies = {
            'privacy_policy': ['privacy', 'privacy-policy'],
            'return_policy': ['return', 'returns', 'return-policy'],
            'refund_policy': ['refund', 'refunds', 'refund-policy']
        }
        
        for policy_type, keywords in policies.items():
            policy_url = None
            policy_text = ""
            
            # Look for policy links
            for keyword in keywords:
                link = soup.find('a', {'href': lambda x: x and keyword in x.lower()})
                if link:
                    policy_url = normalize_url(link.get('href'), website_url)
                    
                    # Try to fetch policy content
                    try:
                        policy_content = self._fetch_page(policy_url)
                        policy_soup = BeautifulSoup(policy_content, 'html.parser')
                        
                        # Remove navigation and footer
                        for element in policy_soup.find_all(['nav', 'header', 'footer']):
                            element.decompose()
                        
                        policy_text = clean_text(policy_soup.get_text())
                        policy_text = truncate_text(policy_text, 2000)
                        
                    except Exception as e:
                        logger.warning(f"Failed to fetch policy {policy_url}: {e}")
                    
                    break
            
            result[f'{policy_type}_url'] = policy_url
            result[f'{policy_type}_text'] = policy_text
        
        return result
    
    def _extract_faqs(self, soup: BeautifulSoup, website_url: str) -> List[Dict[str, str]]:
        """Extract FAQ information"""
        faqs = []
        
        # Look for FAQ sections
        faq_sections = soup.find_all(['section', 'div'], {
            'class': lambda x: x and any(keyword in x.lower() for keyword in ['faq', 'question', 'help'])
        })
        
        for section in faq_sections:
            # Look for question-answer pairs
            questions = section.find_all(['h3', 'h4', 'dt', 'div'], {
                'class': lambda x: x and 'question' in x.lower()
            })
            
            for question in questions:
                question_text = clean_text(question.get_text())
                if not question_text:
                    continue
                
                # Find corresponding answer
                answer_text = ""
                next_element = question.find_next_sibling()
                if next_element:
                    answer_text = clean_text(next_element.get_text())
                
                if question_text and answer_text:
                    faqs.append({
                        'question': question_text,
                        'answer': truncate_text(answer_text, 500)
                    })
        
        return faqs[:10]  # Limit to 10 FAQs
    
    def _extract_hero_products(self, soup: BeautifulSoup, website_url: str) -> List[Dict[str, Any]]:
        """Extract hero products from homepage"""
        hero_products = []
        
        # Look for product sections on homepage
        product_sections = soup.find_all(['section', 'div'], {
            'class': lambda x: x and any(keyword in x.lower() for keyword in ['product', 'featured', 'hero'])
        })
        
        for section in product_sections:
            products = section.find_all(['div', 'article'], {
                'class': lambda x: x and 'product' in x.lower()
            })
            
            for product in products:
                product_data = {}
                
                # Extract product title
                title_elem = product.find(['h1', 'h2', 'h3', 'h4'])
                if title_elem:
                    product_data['title'] = clean_text(title_elem.get_text())
                
                # Extract product link
                link_elem = product.find('a')
                if link_elem:
                    product_data['url'] = normalize_url(link_elem.get('href'), website_url)
                
                # Extract product image
                img_elem = product.find('img')
                if img_elem:
                    product_data['image'] = normalize_url(img_elem.get('src'), website_url)
                
                # Extract price
                price_elem = product.find(['span', 'div'], {
                    'class': lambda x: x and 'price' in x.lower()
                })
                if price_elem:
                    price_text = clean_text(price_elem.get_text())
                    # Extract numeric price
                    import re
                    price_match = re.search(r'[\\$]?([0-9,]+\\.?[0-9]*)', price_text)
                    if price_match:
                        product_data['price'] = price_match.group(1).replace(',', '')
                
                if product_data.get('title'):
                    hero_products.append(product_data)
        
        return hero_products[:5]  # Limit to 5 hero products
    
    def _get_product_catalog(self, website_url: str) -> List[Dict[str, Any]]:
        """Get complete product catalog from Shopify store"""
        products = []
        
        try:
            # Try to get products from /products.json endpoint
            products_url = urljoin(website_url, '/products.json')
            
            page = 1
            while True:
                # Add pagination
                params = {'limit': 250, 'page': page}
                paginated_url = f"{products_url}?{urlencode(params)}"
                
                response_text = self._fetch_page(paginated_url)
                
                try:
                    data = json.loads(response_text)
                    page_products = data.get('products', [])
                    
                    if not page_products:
                        break
                    
                    for product in page_products:
                        product_data = {
                            'shopify_id': product.get('id'),
                            'title': product.get('title'),
                            'handle': product.get('handle'),
                            'description': clean_text(product.get('body_html', '')),
                            'vendor': product.get('vendor'),
                            'product_type': product.get('product_type'),
                            'tags': (
                                    product.get('tags', '').split(',') if isinstance(product.get('tags'), str) and product.get('tags') 
                                    else product.get('tags', []) if isinstance(product.get('tags'), list) 
                                    else []
                                ),
                            'product_url': urljoin(website_url, f"/products/{product.get('handle')}"),
                            'created_at': product.get('created_at'),
                            'updated_at': product.get('updated_at'),
                            'available': product.get('available', True),
                            'variants': product.get('variants', []),
                            'images': product.get('images', []),
                            'options': product.get('options', [])
                        }
                        
                        # Extract price from first variant
                        if product_data['variants']:
                            first_variant = product_data['variants'][0]
                            product_data['price'] = first_variant.get('price')
                            product_data['compare_at_price'] = first_variant.get('compare_at_price')
                        
                        # Extract featured image
                        if product_data['images']:
                            product_data['featured_image'] = product_data['images'][0].get('src')
                        
                        products.append(product_data)
                    
                    page += 1
                    
                    # Add delay between requests
                    time.sleep(Config.DELAY_BETWEEN_REQUESTS)
                    
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse JSON from {paginated_url}")
                    break
                    
        except Exception as e:
            logger.error(f"Failed to get product catalog: {e}")
        
        return products
    
    def get_sitemap_urls(self, website_url: str) -> List[str]:
        """Get URLs from sitemap"""
        urls = []
        
        try:
            sitemap_url = urljoin(website_url, '/sitemap.xml')
            sitemap_content = self._fetch_page(sitemap_url)
            
            soup = BeautifulSoup(sitemap_content, 'xml')
            
            # Check if it's a sitemap index
            sitemaps = soup.find_all('sitemap')
            if sitemaps:
                for sitemap in sitemaps:
                    loc = sitemap.find('loc')
                    if loc:
                        sub_sitemap_url = loc.text
                        try:
                            sub_content = self._fetch_page(sub_sitemap_url)
                            sub_soup = BeautifulSoup(sub_content, 'xml')
                            
                            for url_elem in sub_soup.find_all('url'):
                                loc_elem = url_elem.find('loc')
                                if loc_elem:
                                    urls.append(loc_elem.text)
                        except Exception as e:
                            logger.warning(f"Failed to fetch sub-sitemap {sub_sitemap_url}: {e}")
            else:
                # Direct sitemap
                for url_elem in soup.find_all('url'):
                    loc_elem = url_elem.find('loc')
                    if loc_elem:
                        urls.append(loc_elem.text)
        
        except Exception as e:
            logger.warning(f"Failed to get sitemap URLs: {e}")
        
        return urls