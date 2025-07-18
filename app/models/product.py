from . import db
from datetime import datetime
from sqlalchemy.dialects.mysql import JSON

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=False)
    
    # Product identifiers
    shopify_id = db.Column(db.String(50))
    handle = db.Column(db.String(255))
    
    # Basic product information
    title = db.Column(db.String(512), nullable=False)
    description = db.Column(db.Text)
    vendor = db.Column(db.String(255))
    product_type = db.Column(db.String(255))
    tags = db.Column(JSON)  # Store as JSON array
    
    # Pricing information
    price = db.Column(db.Numeric(10, 2))
    compare_at_price = db.Column(db.Numeric(10, 2))
    
    # Product URLs and images
    product_url = db.Column(db.String(512))
    image_urls = db.Column(JSON)  # Store as JSON array
    featured_image = db.Column(db.String(512))
    
    # Availability
    available = db.Column(db.Boolean, default=True)
    inventory_quantity = db.Column(db.Integer)
    
    # Variants information
    variants = db.Column(JSON)  # Store as JSON array of variant objects
    
    # SEO
    seo_title = db.Column(db.String(255))
    seo_description = db.Column(db.Text)
    
    # Categorization
    is_hero_product = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'brand_id': self.brand_id,
            'shopify_id': self.shopify_id,
            'handle': self.handle,
            'title': self.title,
            'description': self.description,
            'vendor': self.vendor,
            'product_type': self.product_type,
            'tags': self.tags,
            'price': float(self.price) if self.price else None,
            'compare_at_price': float(self.compare_at_price) if self.compare_at_price else None,
            'product_url': self.product_url,
            'image_urls': self.image_urls,
            'featured_image': self.featured_image,
            'available': self.available,
            'inventory_quantity': self.inventory_quantity,
            'variants': self.variants,
            'seo_title': self.seo_title,
            'seo_description': self.seo_description,
            'is_hero_product': self.is_hero_product,
            'created_at': self.created_at if self.created_at else None,
            'updated_at': self.updated_at if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Product {self.title}>'