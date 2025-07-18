from . import db
from datetime import datetime
from sqlalchemy.dialects.mysql import JSON

class Brand(db.Model):
    __tablename__ = 'brands'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    website_url = db.Column(db.String(512), nullable=False, unique=True)
    domain = db.Column(db.String(255), nullable=False)
    
    # Basic brand information
    brand_context = db.Column(db.Text)
    contact_email = db.Column(db.String(255))
    contact_phone = db.Column(db.String(50))
    
    # Social media handles
    social_handles = db.Column(JSON)  # Store as JSON: {"instagram": "@handle", "facebook": "page", ...}
    
    # Policy information
    privacy_policy_url = db.Column(db.String(512))
    privacy_policy_text = db.Column(db.Text)
    return_policy_url = db.Column(db.String(512))
    return_policy_text = db.Column(db.Text)
    refund_policy_url = db.Column(db.String(512))
    refund_policy_text = db.Column(db.Text)
    
    # FAQ information
    faqs = db.Column(JSON)  # Store as JSON array of Q&A objects
    
    # Important links
    important_links = db.Column(JSON)  # Store as JSON: {"order_tracking": "url", "contact_us": "url", ...}
    
    # Hero products (products on homepage)
    hero_products = db.Column(JSON)  # Store as JSON array
    
    # Scraping metadata
    is_shopify_store = db.Column(db.Boolean, default=False)
    last_scraped = db.Column(db.DateTime, default=datetime.utcnow)
    scraping_status = db.Column(db.String(50), default='pending')  # pending, in_progress, completed, failed
    scraping_errors = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', backref='brand', lazy=True, cascade='all, delete-orphan')
    competitors = db.relationship('Competitor', backref='brand', lazy=True, cascade='all, delete-orphan')
    analyses = db.relationship('Analysis', backref='brand', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
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
            'is_shopify_store': self.is_shopify_store,
            'scraping_status': self.scraping_status,
            'created_at': self.created_at if self.created_at else None,
            'updated_at': self.updated_at if self.updated_at else None,
            'last_scraped': self.last_scraped if self.last_scraped else None
        }
    
    def __repr__(self):
        return f'<Brand {self.name}>'