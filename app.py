"""
Flask web application to display Redash query results
"""
import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from flask import Flask, render_template, jsonify, request
from redash_client import RedashClient
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Global variables to store data
cached_data = {}
last_update = None

def load_cached_data() -> Dict[str, Any]:
    """Load cached data from file"""
    global cached_data, last_update
    
    try:
        if os.path.exists(Config.DATA_FILE):
            with open(Config.DATA_FILE, 'r') as f:
                data = json.load(f)
                cached_data = data.get('results', {})
                last_update = data.get('last_update')
                if last_update:
                    last_update = datetime.fromisoformat(last_update)
        else:
            logger.info("No cached data file found")
    except Exception as e:
        logger.error(f"Error loading cached data: {e}")

def save_cached_data(data: Dict[str, Any]) -> None:
    """Save data to cache file"""
    global cached_data, last_update
    
    try:
        # Ensure data directory exists
        os.makedirs(os.path.dirname(Config.DATA_FILE), exist_ok=True)
        
        cached_data = data
        last_update = datetime.now(timezone.utc)
        
        cache_data = {
            'results': cached_data,
            'last_update': last_update.isoformat()
        }
        
        with open(Config.DATA_FILE, 'w') as f:
            json.dump(cache_data, f, indent=2, default=str)
        
        logger.info(f"Data cached successfully at {last_update}")
    except Exception as e:
        logger.error(f"Error saving cached data: {e}")

def format_data_for_display(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Format raw Redash data for web display"""
    if not raw_data or 'query_result' not in raw_data:
        return {'rows': [], 'columns': [], 'error': 'No data available'}
    
    query_result = raw_data['query_result']
    data_dict = query_result.get('data', {})
    
    rows = data_dict.get('rows', [])
    columns = data_dict.get('columns', [])
    
    # Format columns for better display
    formatted_columns = []
    for col in columns:
        formatted_columns.append({
            'name': col.get('name', ''),
            'friendly_name': col.get('friendly_name', col.get('name', '')),
            'type': col.get('type', 'string')
        })
    
    return {
        'rows': rows,
        'columns': formatted_columns,
        'total_rows': len(rows),
        'retrieved_at': query_result.get('retrieved_at'),
        'query_hash': query_result.get('query_hash'),
        'error': None
    }

@app.route('/')
def index():
    """Main page displaying query results"""
    formatted_data = format_data_for_display(cached_data)
    
    return render_template('index.html', 
                         data=formatted_data,
                         last_update=last_update,
                         config=Config)

@app.route('/api/data')
def api_data():
    """API endpoint to get current data as JSON"""
    formatted_data = format_data_for_display(cached_data)
    return jsonify({
        'data': formatted_data,
        'last_update': last_update.isoformat() if last_update else None,
        'query_id': Config.REDASH_QUERY_ID
    })

@app.route('/api/refresh', methods=['POST'])
def api_refresh():
    """API endpoint to manually refresh data"""
    try:
        client = RedashClient()
        
        if not client.test_connection():
            return jsonify({'error': 'Failed to connect to Redash'}), 500
        
        # Fetch fresh data
        fresh_data = client.fetch_fresh_results(Config.REDASH_QUERY_ID)
        if fresh_data:
            save_cached_data(fresh_data)
            return jsonify({'success': True, 'message': 'Data refreshed successfully'})
        else:
            return jsonify({'error': 'Failed to fetch fresh data'}), 500
            
    except Exception as e:
        logger.error(f"Error during manual refresh: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'last_update': last_update.isoformat() if last_update else None,
        'data_available': bool(cached_data)
    })

def initialize_app():
    """Initialize the application"""
    # Load cached data
    load_cached_data()
    
    # If no cached data, try to fetch some
    if not cached_data:
        logger.info("No cached data found, attempting to fetch from Redash...")
        try:
            client = RedashClient()
            if client.test_connection():
                data = client.get_query_results(Config.REDASH_QUERY_ID)
                if data:
                    save_cached_data(data)
                    logger.info("Initial data fetched successfully")
                else:
                    logger.warning("No data could be fetched from Redash")
            else:
                logger.error("Could not connect to Redash during initialization")
        except Exception as e:
            logger.error(f"Error during initialization: {e}")

if __name__ == '__main__':
    # Validate configuration
    if not Config.validate():
        logger.error("Invalid configuration. Please check your settings.")
        exit(1)
    
    # Initialize the app
    initialize_app()
    
    # Run the Flask app
    logger.info(f"Starting web server on {Config.WEB_HOST}:{Config.WEB_PORT}")
    app.run(host=Config.WEB_HOST, port=Config.WEB_PORT, debug=False)