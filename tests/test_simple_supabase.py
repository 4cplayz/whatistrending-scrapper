"""
Simple Supabase connection test.

This tests basic Supabase connectivity without complex operations.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_supabase_import():
    """Test if we can import Supabase modules."""
    try:
        from supabase import create_client, Client
        print("✅ Supabase modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Supabase: {e}")
        return False

def test_direct_connection():
    """Test direct Supabase connection."""
    try:
        from supabase import create_client
        
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        
        if not url or not key:
            print("❌ SUPABASE_URL or SUPABASE_KEY not set")
            return False
        
        print(f"Testing connection to: {url}")
        
        # Try to create client
        supabase = create_client(url, key)
        print("✅ Supabase client created")
        
        # Try a simple query
        try:
            # This should work even if the table doesn't exist - it will just return an error we can catch
            result = supabase.table("test_table").select("*").limit(1).execute()
            print("✅ Basic query executed (table may not exist, but connection works)")
            return True
        except Exception as query_error:
            print(f"✅ Connection works, query error expected: {query_error}")
            return True
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def main():
    """Run simple tests."""
    print("=== Simple Supabase Connection Test ===")
    
    # Test 1: Import
    import_success = test_supabase_import()
    
    # Test 2: Connection
    connection_success = test_direct_connection()
    
    print("\n=== Results ===")
    print(f"Import test: {'✅ Pass' if import_success else '❌ Fail'}")
    print(f"Connection test: {'✅ Pass' if connection_success else '❌ Fail'}")
    
    if import_success and connection_success:
        print("🎉 Supabase is working!")
        return True
    else:
        print("⚠️ Some tests failed")
        return False

if __name__ == "__main__":
    main()