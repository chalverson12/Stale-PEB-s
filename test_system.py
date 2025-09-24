#!/usr/bin/env python3
"""
Test script to verify the Redash to Website system is working correctly
"""
import sys
import os
from datetime import datetime

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    try:
        import requests
        import flask
        import schedule
        print("✅ All required modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def test_configuration():
    """Test configuration validity"""
    print("🔧 Testing configuration...")
    try:
        from config import Config
        
        print(f"   Redash URL: {Config.REDASH_BASE_URL}")
        print(f"   Query ID: {Config.REDASH_QUERY_ID}")
        print(f"   API Key: {'*' * len(Config.REDASH_API_KEY[:-4]) + Config.REDASH_API_KEY[-4:]}")
        
        if Config.validate():
            print("✅ Configuration is valid")
            return True
        else:
            print("❌ Configuration is invalid")
            return False
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_redash_connection():
    """Test connection to Redash"""
    print("🌐 Testing Redash connection...")
    try:
        from redash_client import RedashClient
        
        client = RedashClient()
        if client.test_connection():
            print("✅ Successfully connected to Redash")
            
            # Test query info
            from config import Config
            query_info = client.get_query_info(Config.REDASH_QUERY_ID)
            if query_info:
                print(f"✅ Query found: '{query_info.get('name', 'Unknown')}'")
                
                # Check for parameters
                options = query_info.get('options', {})
                parameters = options.get('parameters', [])
                if parameters:
                    print(f"📊 Query has {len(parameters)} parameters:")
                    for param in parameters:
                        print(f"   - {param.get('name')} ({param.get('type')})")
                
                return True
            else:
                print("❌ Could not retrieve query information")
                return False
        else:
            print("❌ Failed to connect to Redash")
            print("   This might be normal if Redash is on an internal network")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_data_fetch():
    """Test data fetching"""
    print("📊 Testing data fetch...")
    try:
        from redash_client import RedashClient
        
        client = RedashClient()
        
        # Try to get existing results first
        from config import Config
        results = client.get_query_results(Config.REDASH_QUERY_ID)
        if results:
            query_result = results.get('query_result', {})
            data_dict = query_result.get('data', {})
            rows = data_dict.get('rows', [])
            columns = data_dict.get('columns', [])
            
            print(f"✅ Retrieved {len(rows)} rows with {len(columns)} columns")
            
            if columns:
                print("📋 Columns:")
                for col in columns[:5]:  # Show first 5 columns
                    print(f"   - {col.get('name')} ({col.get('type')})")
                if len(columns) > 5:
                    print(f"   ... and {len(columns) - 5} more")
            
            return True
        else:
            print("⚠️  No cached results found")
            print("   Try running: python scheduler.py --once")
            return False
    except Exception as e:
        print(f"❌ Data fetch error: {e}")
        return False

def test_directories():
    """Test that required directories exist"""
    print("📁 Testing directories...")
    try:
        from config import Config
        
        directories = [
            os.path.dirname(Config.DATA_FILE),
            os.path.dirname(Config.LOG_FILE),
            'templates'
        ]
        
        for directory in directories:
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                print(f"✅ Created directory: {directory}")
            else:
                print(f"✅ Directory exists: {directory}")
        
        return True
    except Exception as e:
        print(f"❌ Directory error: {e}")
        return False

def test_web_app():
    """Test that the web app can start"""
    print("🌐 Testing web application...")
    try:
        from app import app
        
        # Test that the app can be created
        with app.test_client() as client:
            response = client.get('/health')
            if response.status_code == 200:
                print("✅ Web application health check passed")
                return True
            else:
                print(f"❌ Health check failed with status {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Web app error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Redash to Website System Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_configuration,
        test_directories,
        test_redash_connection,
        test_data_fetch,
        test_web_app
    ]
    
    results = []
    for test in tests:
        print()
        result = test()
        results.append(result)
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"✅ Passed: {sum(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("\n🎉 All tests passed! Your system is ready to deploy.")
        print("\nNext steps:")
        print("1. Run: python scheduler.py --once  (to fetch initial data)")
        print("2. Run: python app.py  (to start the web server)")
        print("3. Visit: http://localhost:8000")
    else:
        print("\n⚠️  Some tests failed. Please address the issues above.")
        print("\nCommon solutions:")
        print("- Ensure you're on a network that can access redash.zp-int.com")
        print("- Verify your API key has the correct permissions")
        print("- Check that query ID 100778 exists and is accessible")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)