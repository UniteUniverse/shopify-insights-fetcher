from flask import Blueprint, request, jsonify
from app.services.brand_analyzer import BrandAnalyzerService
from app.utils.validators import ShopifyValidator
from app.utils.exceptions import ValidationError
from pydantic import ValidationError as PydanticValidationError
import logging

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)
brand_analyzer = BrandAnalyzerService()

@api_bp.route('/analyze', methods=['POST'])
def analyze_brand():
    """API endpoint for brand analysis"""
    try:
        # Validate request data
        data = request.get_json()
        
        if not data or 'website_url' not in data:
            return jsonify({
                'error': 'Missing required field: website_url',
                'status_code': 400
            }), 400
        
        # Validate URL
        try:
            validator = ShopifyValidator(website_url=data['website_url'])
            website_url = str(validator.website_url)
        except PydanticValidationError as e:
            return jsonify({
                'error': 'Invalid website URL',
                'details': str(e),
                'status_code': 400
            }), 400
        
        # Get options
        include_competitors = data.get('include_competitors', False)
        
        # Perform analysis
        result = brand_analyzer.analyze_brand(website_url, include_competitors)
        
        if 'error' in result:
            return jsonify({
                'error': result['error'],
                'brand_id': result.get('brand_id'),
                'status_code': 500
            }), 500
        
        return jsonify({
            'success': True,
            'brand_id': result['brand_id'],
            'brand_data': result['brand_data'],
            'competitors': result.get('competitors', []),
            'competitive_analysis': result.get('competitive_analysis', {}),
            'status_code': 200
        })
        
    except Exception as e:
        logger.error(f"API analysis failed: {e}")
        return jsonify({
            'error': 'Internal server error',
            'details': str(e),
            'status_code': 500
        }), 500

@api_bp.route('/brands', methods=['GET'])
def get_brands():
    """Get all brands"""
    try:
        brands = brand_analyzer.list_brands()
        return jsonify({
            'success': True,
            'brands': brands,
            'count': len(brands),
            'status_code': 200
        })
    except Exception as e:
        logger.error(f"Failed to get brands: {e}")
        return jsonify({
            'error': 'Failed to retrieve brands',
            'details': str(e),
            'status_code': 500
        }), 500

@api_bp.route('/brand/<int:brand_id>', methods=['GET'])
def get_brand(brand_id):
    """Get brand details"""
    try:
        brand_data = brand_analyzer.get_brand_analysis(brand_id)
        return jsonify({
            'success': True,
            'data': brand_data,
            'status_code': 200
        })
    except Exception as e:
        logger.error(f"Failed to get brand {brand_id}: {e}")
        return jsonify({
            'error': 'Brand not found',
            'details': str(e),
            'status_code': 404
        }), 404

@api_bp.route('/brand/<int:brand_id>', methods=['DELETE'])
def delete_brand(brand_id):
    """Delete a brand"""
    try:
        if brand_analyzer.delete_brand(brand_id):
            return jsonify({
                'success': True,
                'message': 'Brand deleted successfully',
                'status_code': 200
            })
        else:
            return jsonify({
                'error': 'Failed to delete brand',
                'status_code': 500
            }), 500
    except Exception as e:
        logger.error(f"Failed to delete brand {brand_id}: {e}")
        return jsonify({
            'error': 'Failed to delete brand',
            'details': str(e),
            'status_code': 500
        }), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Shopify Insights Fetcher',
        'version': '1.0.0'
    })

@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'status_code': 404
    }), 404

@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'status_code': 500
    }), 500