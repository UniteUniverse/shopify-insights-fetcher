from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .brand import Brand
from .product import Product
from .competitor import Competitor
from .analysis import Analysis

__all__ = ['db', 'Brand', 'Product', 'Competitor', 'Analysis']