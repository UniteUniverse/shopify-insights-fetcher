class ScrapingError(Exception):
    """Base exception for scraping errors"""
    pass

class ValidationError(Exception):
    """Exception for validation errors"""
    pass

class LLMError(Exception):
    """Exception for LLM processing errors"""
    pass

class ShopifyDetectionError(ScrapingError):
    """Exception for Shopify detection errors"""
    pass

class RateLimitError(ScrapingError):
    """Exception for rate limiting errors"""
    pass

class NetworkError(ScrapingError):
    """Exception for network errors"""
    pass

class ParseError(ScrapingError):
    """Exception for parsing errors"""
    pass

class DatabaseError(Exception):
    """Exception for database errors"""
    pass

class ConfigurationError(Exception):
    """Exception for configuration errors"""
    pass