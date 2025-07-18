from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.brand_analyzer import BrandAnalyzerService
from app.models import Brand
import logging

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)
brand_analyzer = BrandAnalyzerService()

@main_bp.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@main_bp.route('/analyze', methods=['GET', 'POST'])
def analyze():
    """Brand analysis page"""
    if request.method == 'POST':
        website_url = request.form.get('website_url')
        include_competitors = request.form.get('include_competitors') == 'on'
        
        if not website_url:
            flash('Please enter a website URL', 'error')
            return redirect(url_for('main.analyze'))
        
        try:
            # Start analysis
            result = brand_analyzer.analyze_brand(website_url, include_competitors)
            
            if 'error' in result:
                flash(f'Analysis failed: {result["error"]}', 'error')
                return redirect(url_for('main.analyze'))
            
            flash('Analysis completed successfully!', 'success')
            return redirect(url_for('main.brand_detail', brand_id=result['brand_id']))
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            flash(f'Analysis failed: {str(e)}', 'error')
            return redirect(url_for('main.analyze'))
    
    return render_template('analyze.html')

@main_bp.route('/brands')
def brands():
    """List all brands"""
    brands_data = brand_analyzer.list_brands()
    return render_template('brands.html', brands=brands_data)

@main_bp.route('/brand/<int:brand_id>')
def brand_detail(brand_id):
    """Brand detail page"""
    try:
        brand_data = brand_analyzer.get_brand_analysis(brand_id)
        return render_template('brand_detail.html', data=brand_data)
    except Exception as e:
        logger.error(f"Failed to get brand detail: {e}")
        flash('Brand not found', 'error')
        return redirect(url_for('main.brands'))

@main_bp.route('/brand/<int:brand_id>/delete', methods=['POST'])
def delete_brand(brand_id):
    """Delete a brand"""
    try:
        if brand_analyzer.delete_brand(brand_id):
            flash('Brand deleted successfully', 'success')
        else:
            flash('Failed to delete brand', 'error')
    except Exception as e:
        logger.error(f"Failed to delete brand: {e}")
        flash('Failed to delete brand', 'error')
    
    return redirect(url_for('main.brands'))