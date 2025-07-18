from urllib.parse import urlparse, urljoin
import re
import html
from typing import Optional, List, Dict, Any

def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    parsed = urlparse(url)
    return parsed.netloc.lower()

def normalize_url(url: str, base_url: str = None) -> str:
    """Normalize URL and resolve relative URLs"""
    if base_url and not url.startswith(('http://', 'https://')):
        url = urljoin(base_url, url)
    return url.rstrip('/')

def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    if not text:
        return ""
    
    # Decode HTML entities
    text = html.unescape(text)
    
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text

def extract_phone_numbers(text: str) -> List[str]:
    """Extract phone numbers from text"""
    if not text:
        return []
    
    # Pattern for phone numbers
    phone_pattern = r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
    matches = re.findall(phone_pattern, text)
    
    phones = []
    for match in matches:
        phone = ''.join(match)
        phone = re.sub(r'[^\d+]', '', phone)
        if len(phone) >= 10:
            phones.append(phone)
    
    return list(set(phones))

def extract_email_addresses(text: str) -> List[str]:
    """Extract email addresses from text"""
    if not text:
        return []
    
    # Pattern for email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(email_pattern, text)
    
    return list(set(matches))

def extract_social_handles(text: str, html_content: str = None) -> Dict[str, str]:
    """Extract social media handles from text and HTML"""
    social_handles = {}
    
    # Common social media patterns
    patterns = {
        'instagram': [
            r'instagram\.com/([a-zA-Z0-9_.]+)',
            r'@([a-zA-Z0-9_.]+)',
            r'instagram\.com/([a-zA-Z0-9_.]+)'
        ],
        'facebook': [
            r'facebook\.com/([a-zA-Z0-9_.]+)',
            r'fb\.com/([a-zA-Z0-9_.]+)'
        ],
        'twitter': [
            r'twitter\.com/([a-zA-Z0-9_.]+)',
            r'x\.com/([a-zA-Z0-9_.]+)'
        ],
        'tiktok': [
            r'tiktok\.com/@([a-zA-Z0-9_.]+)',
            r'tiktok\.com/([a-zA-Z0-9_.]+)'
        ],
        'youtube': [
            r'youtube\.com/channel/([a-zA-Z0-9_.]+)',
            r'youtube\.com/user/([a-zA-Z0-9_.]+)',
            r'youtube\.com/@([a-zA-Z0-9_.]+)'
        ],
        'linkedin': [
            r'linkedin\.com/company/([a-zA-Z0-9_.]+)',
            r'linkedin\.com/in/([a-zA-Z0-9_.]+)'
        ]
    }
    
    search_text = text
    if html_content:
        search_text += " " + html_content
    
    for platform, platform_patterns in patterns.items():
        for pattern in platform_patterns:
            matches = re.findall(pattern, search_text, re.IGNORECASE)
            if matches:
                social_handles[platform] = matches[0]
                break
    
    return social_handles

def is_shopify_store(html_content: str, url: str = None) -> bool:
    """Check if a website is a Shopify store"""
    if not html_content:
        return False
    
    # Check for Shopify indicators
    shopify_indicators = [
        'Shopify.theme',
        'shopify.com',
        'shopify-analytics',
        'cdn.shopify.com',
        'myshopify.com',
        'Shopify.shop',
        'window.Shopify'
    ]
    
    for indicator in shopify_indicators:
        if indicator in html_content:
            return True
    
    # Check URL patterns
    if url and 'myshopify.com' in url:
        return True
    
    return False

def extract_important_links(html_content: str, base_url: str) -> Dict[str, str]:
    """Extract important links from HTML content"""
    important_links = {}
    
    # Common important link patterns
    link_patterns = {
        'contact_us': [
            r'href="([^"]*contact[^"]*)"',
            r'href="([^"]*about[^"]*)"'
        ],
        'order_tracking': [
            r'href="([^"]*track[^"]*)"',
            r'href="([^"]*order[^"]*)"'
        ],
        'shipping': [
            r'href="([^"]*shipping[^"]*)"',
            r'href="([^"]*delivery[^"]*)"'
        ],
        'returns': [
            r'href="([^"]*return[^"]*)"',
            r'href="([^"]*refund[^"]*)"'
        ],
        'faq': [
            r'href="([^"]*faq[^"]*)"',
            r'href="([^"]*help[^"]*)"'
        ],
        'blog': [
            r'href="([^"]*blog[^"]*)"',
            r'href="([^"]*news[^"]*)"'
        ]
    }
    
    for link_type, patterns in link_patterns.items():
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                url = normalize_url(matches[0], base_url)
                important_links[link_type] = url
                break
    
    return important_links

def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to specified length"""
    if not text or len(text) <= max_length:
        return text
    
    # Try to truncate at word boundary
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length * 0.8:  # If we can find a space in the last 20%
        truncated = truncated[:last_space]
    
    return truncated + "..."

def format_price(price: float) -> str:
    """Format price for display"""
    if price is None:
        return "N/A"
    return f"${price:.2f}"

def validate_url_format(url: str) -> bool:
    """Validate URL format"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False