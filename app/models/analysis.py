from . import db
from datetime import datetime
from sqlalchemy.dialects.mysql import JSON

class Analysis(db.Model):
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=False)
    
    # Analysis information
    analysis_type = db.Column(db.String(100), nullable=False)  # 'brand_analysis', 'competitor_analysis', etc.
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # Analysis results
    results = db.Column(JSON)  # Store structured analysis results
    insights = db.Column(JSON)  # Store key insights
    recommendations = db.Column(JSON)  # Store recommendations
    
    # Metadata
    analysis_status = db.Column(db.String(50), default='pending')  # pending, in_progress, completed, failed
    processing_time = db.Column(db.Integer)  # Time taken in seconds
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'brand_id': self.brand_id,
            'analysis_type': self.analysis_type,
            'title': self.title,
            'description': self.description,
            'results': self.results,
            'insights': self.insights,
            'recommendations': self.recommendations,
            'analysis_status': self.analysis_status,
            'processing_time': self.processing_time,
            'created_at': self.created_at if self.created_at else None,
            'updated_at': self.updated_at if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Analysis {self.title}>'