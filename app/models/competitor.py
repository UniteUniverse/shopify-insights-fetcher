from . import db
from datetime import datetime
from sqlalchemy.dialects.mysql import JSON

class Competitor(db.Model):
    __tablename__ = 'competitors'
    
    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=False)
    
    # Competitor information
    name = db.Column(db.String(255), nullable=False)
    website_url = db.Column(db.String(512), nullable=False)
    domain = db.Column(db.String(255), nullable=False)
    
    # Analysis data (same structure as Brand)
    brand_context = db.Column(db.Text)
    contact_email = db.Column(db.String(255))
    contact_phone = db.Column(db.String(50))
    social_handles = db.Column(JSON)
    
    # Policies
    privacy_policy_url = db.Column(db.String(512))
    privacy_policy_text = db.Column(db.Text)
    return_policy_url = db.Column(db.String(512))
    return_policy_text = db.Column(db.Text)
    refund_policy_url = db.Column(db.String(512))
    refund_policy_text = db.Column(db.Text)
    
    # FAQ and links
    faqs = db.Column(JSON)
    important_links = db.Column(JSON)
    hero_products = db.Column(JSON)
    
    # Competitor-specific data
    estimated_revenue = db.Column(db.String(100))
    market_position = db.Column(db.String(100))
    
    # Scraping metadata
    is_shopify_store = db.Column(db.Boolean, default=False)
    last_scraped = db.Column(db.DateTime, default=datetime.utcnow)
    scraping_status = db.Column(db.String(50), default='pending')
    scraping_errors = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'brand_id': self.brand_id,
            'name': self.name,
            'website_url': self.website_url,
            'domain': self.domain,
            'brand_context': self.brand_context,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'social_handles': self.social_handles,
            'privacy_policy_url': self.privacy_policy_url,
            'privacy_policy_text': self.privacy_policy_text,
            'return_policy_url': self.return_policy_url,
            'return_policy_text': self.return_policy_text,
            'refund_policy_url': self.refund_policy_url,
            'refund_policy_text': self.refund_policy_text,
            'faqs': self.faqs,
            'important_links': self.important_links,
            'hero_products': self.hero_products,
            'estimated_revenue': self.estimated_revenue,
            'market_position': self.market_position,
            'is_shopify_store': self.is_shopify_store,
            'scraping_status': self.scraping_status,
            'created_at': self.created_at if self.created_at else None,
            'updated_at': self.updated_at if self.updated_at else None,
            'last_scraped': self.last_scraped if self.last_scraped else None
        }
    
    def __repr__(self):
        return f'<Competitor {self.name}>'