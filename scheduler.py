"""
Scheduler to automatically refresh Redash query data daily at 10am PST
"""
import os
import json
import logging
import schedule
import time
from datetime import datetime, timezone
from redash_client import RedashClient
from config import Config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def ensure_directories():
    """Ensure required directories exist"""
    directories = [
        os.path.dirname(Config.DATA_FILE),
        os.path.dirname(Config.LOG_FILE)
    ]
    
    for directory in directories:
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")

def refresh_data_job():
    """Job function to refresh data from Redash"""
    logger.info("Starting scheduled data refresh...")
    
    try:
        # Initialize Redash client
        client = RedashClient()
        
        # Test connection
        if not client.test_connection():
            logger.error("Failed to connect to Redash API")
            return False
        
        # Fetch fresh data
        logger.info(f"Fetching fresh data for query ID: {Config.REDASH_QUERY_ID}")
        fresh_data = client.fetch_fresh_results(Config.REDASH_QUERY_ID)
        
        if fresh_data:
            # Save the data
            cache_data = {
                'results': fresh_data,
                'last_update': datetime.now(timezone.utc).isoformat()
            }
            
            with open(Config.DATA_FILE, 'w') as f:
                json.dump(cache_data, f, indent=2, default=str)
            
            # Log success
            query_result = fresh_data.get('query_result', {})
            data_dict = query_result.get('data', {})
            row_count = len(data_dict.get('rows', []))
            
            logger.info(f"Data refresh completed successfully. Retrieved {row_count} rows.")
            return True
        else:
            logger.error("Failed to fetch fresh data from Redash")
            return False
            
    except Exception as e:
        logger.error(f"Error during scheduled refresh: {e}")
        return False

def run_scheduler():
    """Run the scheduler continuously"""
    logger.info("Starting scheduler...")
    logger.info(f"Scheduled to refresh data daily at {Config.REFRESH_TIME_PST} PST")
    
    # Ensure directories exist
    ensure_directories()
    
    # Schedule the job
    schedule.every().day.at(Config.REFRESH_TIME_PST).do(refresh_data_job)
    
    # Run initial refresh if no data exists
    if not os.path.exists(Config.DATA_FILE):
        logger.info("No existing data found. Running initial refresh...")
        refresh_data_job()
    
    # Keep the scheduler running
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            break
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            time.sleep(60)  # Wait a minute before retrying

def run_one_time_refresh():
    """Run a one-time refresh (useful for testing)"""
    logger.info("Running one-time data refresh...")
    ensure_directories()
    success = refresh_data_job()
    
    if success:
        logger.info("One-time refresh completed successfully")
        return True
    else:
        logger.error("One-time refresh failed")
        return False

if __name__ == "__main__":
    import sys
    
    # Validate configuration
    if not Config.validate():
        logger.error("Invalid configuration. Please check your settings.")
        sys.exit(1)
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # Run one-time refresh
        success = run_one_time_refresh()
        sys.exit(0 if success else 1)
    else:
        # Run continuous scheduler
        run_scheduler()