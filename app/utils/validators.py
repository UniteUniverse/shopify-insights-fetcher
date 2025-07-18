from pydantic import BaseModel, validator, HttpUrl
from typing import Optional, List, Dict, Any
import re
from urllib.parse import urlparse

class URLValidator(BaseModel):
    url: HttpUrl
    
    @validator('url')
    def validate_url(cls, v):
        if not str(v).startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v

class ShopifyValidator(BaseModel):
    website_url: HttpUrl
    
    @validator('website_url')
    def validate_shopify_url(cls, v):
        url_str = str(v)
        # Check if it's a valid URL
        if not url_str.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        
        # Basic domain validation
        parsed = urlparse(url_str)
        if not parsed.netloc:
            raise ValueError('Invalid URL format')
        
        return v

class BrandContextModel(BaseModel):
    name: Optional[str] = None
    website_url: HttpUrl
    domain: str
    brand_context: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    social_handles: Optional[Dict[str, str]] = None
    privacy_policy_url: Optional[str] = None
    privacy_policy_text: Optional[str] = None
    return_policy_url: Optional[str] = None
    return_policy_text: Optional[str] = None
    refund_policy_url: Optional[str] = None
    refund_policy_text: Optional[str] = None
    faqs: Optional[List[Dict[str, str]]] = None
    important_links: Optional[Dict[str, str]] = None
    hero_products: Optional[List[Dict[str, Any]]] = None
    is_shopify_store: bool = False
    
    @validator('contact_email')
    def validate_email(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v
    
    @validator('contact_phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^[\+]?[\d\s\-\(\)]+$', v):
            raise ValueError('Invalid phone format')
        return v

class ProductModel(BaseModel):
    title: str
    description: Optional[str] = None
    vendor: Optional[str] = None
    product_type: Optional[str] = None
    tags: Optional[List[str]] = None
    price: Optional[float] = None
    compare_at_price: Optional[float] = None
    product_url: Optional[str] = None
    image_urls: Optional[List[str]] = None
    featured_image: Optional[str] = None
    available: bool = True
    inventory_quantity: Optional[int] = None
    variants: Optional[List[Dict[str, Any]]] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    is_hero_product: bool = False
    
    @validator('price', 'compare_at_price')
    def validate_price(cls, v):
        if v is not None and v < 0:
            raise ValueError('Price cannot be negative')
        return v
    
    @validator('inventory_quantity')
    def validate_inventory(cls, v):
        if v is not None and v < 0:
            raise ValueError('Inventory quantity cannot be negative')
        return v

class CompetitorModel(BaseModel):
    name: str
    website_url: HttpUrl
    domain: str
    brand_context: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    social_handles: Optional[Dict[str, str]] = None
    privacy_policy_url: Optional[str] = None
    privacy_policy_text: Optional[str] = None
    return_policy_url: Optional[str] = None
    return_policy_text: Optional[str] = None
    refund_policy_url: Optional[str] = None
    refund_policy_text: Optional[str] = None
    faqs: Optional[List[Dict[str, str]]] = None
    important_links: Optional[Dict[str, str]] = None
    hero_products: Optional[List[Dict[str, Any]]] = None
    estimated_revenue: Optional[str] = None
    market_position: Optional[str] = None
    is_shopify_store: bool = False
    
    @validator('contact_email')
    def validate_email(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v