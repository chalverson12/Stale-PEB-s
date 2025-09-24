"""
Configuration file for Redash to Website integration
"""
import os
from typing import Optional

class Config:
    # Redash Configuration
    REDASH_BASE_URL: str = os.getenv('REDASH_BASE_URL', 'https://your-redash-instance.com')
    REDASH_API_KEY: str = os.getenv('REDASH_API_KEY', 'ofytSWp0O5riMpC3ldRrJy0sCndu2H9jYEqkfLG1')
    REDASH_QUERY_ID: int = int(os.getenv('REDASH_QUERY_ID', '0'))
    
    # Scheduling Configuration
    REFRESH_TIME_PST: str = "10:00"  # 10:00 AM PST
    TIMEZONE: str = "America/Los_Angeles"
    
    # Web Application Configuration
    WEB_PORT: int = int(os.getenv('WEB_PORT', '8000'))
    WEB_HOST: str = os.getenv('WEB_HOST', '0.0.0.0')
    
    # Data Storage
    DATA_FILE: str = os.getenv('DATA_FILE', 'data/query_results.json')
    LOG_FILE: str = os.getenv('LOG_FILE', 'logs/app.log')
    
    # Website Configuration
    SITE_TITLE: str = os.getenv('SITE_TITLE', 'Redash Query Results')
    SITE_DESCRIPTION: str = os.getenv('SITE_DESCRIPTION', 'Daily updated query results from Redash')
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        if not cls.REDASH_BASE_URL or cls.REDASH_BASE_URL == 'https://your-redash-instance.com':
            return False
        if not cls.REDASH_API_KEY or cls.REDASH_API_KEY == 'your-api-key-here':
            return False
        if cls.REDASH_QUERY_ID == 0:
            return False
        return True