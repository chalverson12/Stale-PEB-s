"""
Redash API client for fetching query results
"""
import requests
import json
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedashClient:
    def __init__(self):
        self.base_url = Config.REDASH_BASE_URL.rstrip('/')
        self.api_key = Config.REDASH_API_KEY
        self.headers = {
            'Authorization': f'Key {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def test_connection(self) -> bool:
        """Test the connection to Redash API"""
        try:
            response = requests.get(
                f"{self.base_url}/api/queries",
                headers=self.headers,
                timeout=30
            )
            return response.status_code == 200
        except requests.RequestException as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_query_info(self, query_id: int) -> Optional[Dict[str, Any]]:
        """Get information about a specific query"""
        try:
            response = requests.get(
                f"{self.base_url}/api/queries/{query_id}",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get query info for ID {query_id}: {e}")
            return None
    
    def refresh_query(self, query_id: int, parameters: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Trigger a query refresh and return the job ID"""
        try:
            payload = {}
            if parameters:
                payload['parameters'] = parameters
            
            response = requests.post(
                f"{self.base_url}/api/queries/{query_id}/refresh",
                headers=self.headers,
                json=payload if payload else None,
                timeout=30
            )
            response.raise_for_status()
            job_data = response.json()
            return job_data.get('job', {}).get('id')
        except requests.RequestException as e:
            logger.error(f"Failed to refresh query {query_id}: {e}")
            return None
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a query job"""
        try:
            response = requests.get(
                f"{self.base_url}/api/jobs/{job_id}",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get job status for {job_id}: {e}")
            return None
    
    def wait_for_query_completion(self, job_id: str, max_wait_time: int = 300) -> bool:
        """Wait for a query to complete execution"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            job_status = self.get_job_status(job_id)
            if not job_status:
                return False
            
            status = job_status.get('job', {}).get('status')
            logger.info(f"Query job {job_id} status: {status}")
            
            if status == 3:  # Completed successfully
                return True
            elif status == 4:  # Failed
                logger.error(f"Query job {job_id} failed")
                return False
            
            time.sleep(5)  # Wait 5 seconds before checking again
        
        logger.error(f"Query job {job_id} timed out after {max_wait_time} seconds")
        return False
    
    def get_query_results(self, query_id: int) -> Optional[Dict[str, Any]]:
        """Get the latest results for a query"""
        try:
            # First try to get cached results
            response = requests.get(
                f"{self.base_url}/api/queries/{query_id}/results",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get query results for ID {query_id}: {e}")
            return None
    
    def get_dynamic_parameters(self, query_id: int) -> Dict[str, Any]:
        """Generate dynamic parameters for queries with date ranges"""
        # Get query info to understand parameters
        query_info = self.get_query_info(query_id)
        if not query_info:
            return {}
        
        # Extract parameter information
        options = query_info.get('options', {})
        parameters = options.get('parameters', [])
        
        dynamic_params = {}
        
        # Handle date range parameters
        for param in parameters:
            param_name = param.get('name', '')
            param_type = param.get('type', 'text')
            
            if param_type == 'date' or 'date' in param_name.lower():
                if 'start' in param_name.lower():
                    # For start date, use 7 days ago
                    dynamic_params[param_name] = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                elif 'end' in param_name.lower():
                    # For end date, use today
                    dynamic_params[param_name] = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"Generated dynamic parameters: {dynamic_params}")
        return dynamic_params
    
    def fetch_fresh_results(self, query_id: int, custom_parameters: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Fetch fresh query results by triggering a refresh"""
        logger.info(f"Fetching fresh results for query {query_id}")
        
        # Get parameters
        if custom_parameters:
            parameters = custom_parameters
        else:
            parameters = self.get_dynamic_parameters(query_id)
        
        # Trigger query refresh
        job_id = self.refresh_query(query_id, parameters)
        if not job_id:
            logger.error("Failed to trigger query refresh")
            return None
        
        # Wait for completion
        if not self.wait_for_query_completion(job_id):
            logger.error("Query execution failed or timed out")
            return None
        
        # Get the results
        return self.get_query_results(query_id)
    
    def get_query_visualization_data(self, query_id: int) -> Optional[List[Dict[str, Any]]]:
        """Get visualization data for a query"""
        try:
            query_info = self.get_query_info(query_id)
            if not query_info:
                return None
            
            visualizations = query_info.get('visualizations', [])
            return visualizations
        except Exception as e:
            logger.error(f"Failed to get visualization data: {e}")
            return None

def main():
    """Test the Redash client"""
    client = RedashClient()
    
    # Test connection
    if not client.test_connection():
        logger.error("Failed to connect to Redash. Please check your configuration.")
        return
    
    logger.info("Successfully connected to Redash!")
    
    # Test with a query ID (you'll need to set this)
    if Config.REDASH_QUERY_ID > 0:
        query_info = client.get_query_info(Config.REDASH_QUERY_ID)
        if query_info:
            logger.info(f"Query '{query_info.get('name')}' found")
        
        results = client.get_query_results(Config.REDASH_QUERY_ID)
        if results:
            logger.info(f"Retrieved {len(results.get('query_result', {}).get('data', {}).get('rows', []))} rows")

if __name__ == "__main__":
    main()