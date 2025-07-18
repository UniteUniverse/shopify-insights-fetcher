# Shopify Insights Fetcher

A comprehensive Flask application for analyzing Shopify stores and extracting detailed insights about brands, products, competitors, and market positioning.

## Features

### Core Features
- **Brand Analysis**: Extract comprehensive brand information including context, contact details, and policies
- **Product Catalog**: Complete product extraction via Shopify's `/products.json` endpoint
- **Hero Products**: Identify products featured on the homepage
- **Contact Information**: Automatic extraction of email addresses and phone numbers
- **Social Media**: Detect and extract social media handles
- **Policy Extraction**: Scrape privacy, return, and refund policies
- **FAQ Mining**: Extract and structure frequently asked questions
- **Important Links**: Discover key navigation links

### Advanced Features
- **Competitor Analysis**: Identify and analyze competitors
- **LLM Integration**: AI-powered insights and recommendations using OpenAI GPT
- **Shopify Detection**: Automatically identify if a site is powered by Shopify
- **Database Persistence**: Store all analysis results in MySQL database
- **RESTful API**: Complete API for programmatic access
- **Web Interface**: User-friendly web interface for manual analysis

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: MySQL with SQLAlchemy ORM
- **Validation**: Pydantic models
- **Web Scraping**: BeautifulSoup + Requests
- **LLM Integration**: OpenAI GPT API
- **Frontend**: Bootstrap 5 + Vanilla JavaScript
- **Deployment**: Gunicorn ready

## Installation

### Prerequisites
- Python 3.8+
- MySQL 5.7+
- OpenAI API key (optional, for LLM features)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/UniteUniverse/shopify-insights-fetcher.git
   cd shopify-insights-fetcher
   ```

2. **Create virtual environment**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**
   ```bash
   mysql -u root -p < database.sql
   ```

5. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. **Initialize Database**
   ```bash
   python -c "from app import create_app; from app.models import db; app = create_app(); app.app_context().push(); db.create_all()"
   ```

7. **Run the application**
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:5000`

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Database Configuration
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=shopify_insights

# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# LLM Configuration (Optional)
OPENAI_API_KEY=your-openai-api-key
```

### MySQL Database

The application requires a MySQL database. Create the database and tables using the provided `database.sql` file.

## API Documentation

### Endpoints

#### Analyze Brand
```
POST /api/analyze
Content-Type: application/json

{
    "website_url": "https://example.com",
    "include_competitors": true
}
```

#### Get All Brands
```
GET /api/brands
```

#### Get Brand Details
```
GET /api/brand/<brand_id>
```

#### Delete Brand
```
DELETE /api/brand/<brand_id>
```

#### Health Check
```
GET /api/health
```

### Example API Usage

```python
import requests

# Analyze a brand
response = requests.post('http://localhost:5000/api/analyze', json={
    'website_url': 'https://gymshark.com',
    'include_competitors': True
})

data = response.json()
print(data)
```

## Usage

### Web Interface

1. Navigate to `http://localhost:5000`
2. Click "Start Analysis"
3. Enter a Shopify store URL
4. Optionally enable competitor analysis
5. View results on the brand detail page

### API Usage

Use the RESTful API for programmatic access:

```bash
# Analyze a brand
curl -X POST http://localhost:5000/api/analyze \\
  -H "Content-Type: application/json" \\
  -d '{"website_url": "https://example.com"}'

# Get all brands
curl http://localhost:5000/api/brands

# Get brand details
curl http://localhost:5000/api/brand/1
```

## Architecture

### Project Structure
```
shopify-insights-fetcher/
├── app/
│   ├── models/          # SQLAlchemy models
│   ├── routes/          # Flask routes
│   ├── services/        # Business logic
│   ├── utils/           # Utilities and helpers
│   ├── templates/       # HTML templates
│   └── static/          # CSS, JS, images
├── config/              # Configuration files
├── tests/               # Test files
├── logs/                # Log files
└── requirements.txt     # Dependencies
```

### Key Components

1. **Scraper Service**: Handles web scraping and data extraction
2. **LLM Processor**: Integrates with OpenAI for insights
3. **Competitor Analyzer**: Identifies and analyzes competitors
4. **Brand Analyzer**: Main orchestrator service
5. **Database Models**: SQLAlchemy models for data persistence

## Best Practices

### Web Scraping Ethics
- Respects robots.txt files
- Implements rate limiting
- Uses appropriate delays between requests
- Handles errors gracefully

### Data Validation
- Pydantic models for request/response validation
- Input sanitization
- Error handling at all levels

### Performance
- Database indexing for fast queries
- Efficient scraping algorithms
- Asynchronous processing capabilities

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check MySQL service is running
   - Verify database credentials in `.env`
   - Ensure database exists

2. **Scraping Failures**
   - Check internet connection
   - Verify target website is accessible
   - Review rate limiting settings

3. **LLM Processing Issues**
   - Verify OpenAI API key is set
   - Check API quota limits
   - Review error logs

### Logs

Check the `logs/` directory for detailed error information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with proper tests
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please create an issue in the repository.
