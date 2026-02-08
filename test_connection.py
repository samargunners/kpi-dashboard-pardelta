"""
Supabase Connection Troubleshooter

This script tests your Supabase connection and verifies data availability.
Run this before starting the dashboard to ensure everything is configured correctly.
"""

import sys
from pathlib import Path

def test_imports():
    """Test if all required packages are installed."""
    print("📦 Testing imports...")
    
    try:
        import streamlit
        print(f"  ✓ streamlit {streamlit.__version__}")
    except ImportError:
        print("  ✗ streamlit not installed")
        return False
    
    try:
        import pandas
        print(f"  ✓ pandas {pandas.__version__}")
    except ImportError:
        print("  ✗ pandas not installed")
        return False
    
    try:
        import supabase
        print(f"  ✓ supabase installed")
    except ImportError:
        print("  ✗ supabase not installed")
        return False
    
    try:
        import psycopg2
        print(f"  ✓ psycopg2 {psycopg2.__version__}")
    except ImportError:
        print("  ✗ psycopg2 not installed")
        return False
    
    print()
    return True


def test_secrets():
    """Test if secrets.toml exists and is valid."""
    print("🔑 Testing secrets configuration...")
    
    secrets_path = Path(".streamlit/secrets.toml")
    
    if not secrets_path.exists():
        print(f"  ✗ secrets.toml not found at {secrets_path}")
        print("  → Run: cp .streamlit/secrets.toml.template .streamlit/secrets.toml")
        return False
    
    print(f"  ✓ secrets.toml found")
    
    # Read and check content
    content = secrets_path.read_text()
    
    has_api = "supabase_url" in content and "supabase_anon_key" in content
    has_pg = "[supabase]" in content and "host" in content
    
    if has_api:
        if "your-project.supabase.co" in content:
            print("  ⚠ API config looks like template - update with real credentials")
        else:
            print("  ✓ API config found")
    
    if has_pg:
        if "your-project" in content or "your-password" in content:
            print("  ⚠ PostgreSQL config looks like template - update with real credentials")
        else:
            print("  ✓ PostgreSQL config found")
    
    if not has_api and not has_pg:
        print("  ✗ No valid configuration found")
        return False
    
    print()
    return True


def test_supabase_api():
    """Test Supabase API connection."""
    print("🌐 Testing Supabase API connection...")
    
    try:
        import toml
        from supabase import create_client
        
        secrets = toml.load(".streamlit/secrets.toml")
        url = secrets.get("supabase_url")
        key = secrets.get("supabase_anon_key")
        
        if not url or not key:
            print("  ⊘ API config not found in secrets")
            return False
        
        if "your-project" in url:
            print("  ⊘ API config still contains template values")
            return False
        
        client = create_client(url, key)
        print(f"  ✓ API client created")
        
        # Try a simple query
        response = client.table("hme_report").select("count", count="exact").limit(0).execute()
        count = response.count if hasattr(response, 'count') else 0
        print(f"  ✓ Connected to database ({count} HME records)")
        
        return True
        
    except Exception as e:
        print(f"  ✗ API connection failed: {e}")
        return False


def test_postgresql():
    """Test PostgreSQL direct connection."""
    print("🐘 Testing PostgreSQL connection...")
    
    try:
        import toml
        import psycopg2
        
        secrets = toml.load(".streamlit/secrets.toml")
        supabase = secrets.get("supabase", {})
        
        host = supabase.get("host")
        database = supabase.get("database") or supabase.get("dbname")
        user = supabase.get("user")
        password = supabase.get("password")
        port = supabase.get("port", 5432)
        
        if not all([host, database, user, password]):
            print("  ⊘ PostgreSQL config incomplete")
            return False
        
        if "your-project" in host or "your-password" in password:
            print("  ⊘ PostgreSQL config still contains template values")
            return False
        
        conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port
        )
        print(f"  ✓ Connected to {host}")
        
        # Test a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM hme_report")
        count = cursor.fetchone()[0]
        print(f"  ✓ Database accessible ({count} HME records)")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"  ✗ PostgreSQL connection failed: {e}")
        return False


def test_data_availability():
    """Test if required tables have data."""
    print("📊 Testing data availability...")
    
    try:
        import toml
        import psycopg2
        from datetime import datetime, timedelta
        
        secrets = toml.load(".streamlit/secrets.toml")
        supabase = secrets.get("supabase", {})
        
        conn = psycopg2.connect(
            host=supabase.get("host"),
            database=supabase.get("database") or supabase.get("dbname"),
            user=supabase.get("user"),
            password=supabase.get("password"),
            port=supabase.get("port", 5432)
        )
        
        cursor = conn.cursor()
        
        # Check recent data (last 7 days)
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        # HME data
        cursor.execute("SELECT COUNT(*) FROM hme_report WHERE date >= %s", (week_ago,))
        hme_count = cursor.fetchone()[0]
        print(f"  HME Report: {hme_count} records (last 7 days)")
        
        # Labor data
        cursor.execute("SELECT COUNT(*) FROM labor_metrics WHERE date >= %s", (week_ago,))
        labor_count = cursor.fetchone()[0]
        print(f"  Labor Metrics: {labor_count} records (last 7 days)")
        
        # Medallia data
        cursor.execute("SELECT COUNT(*) FROM medallia_report WHERE report_date >= %s", (week_ago,))
        medallia_count = cursor.fetchone()[0]
        print(f"  Medallia Report: {medallia_count} records (last 7 days)")
        
        cursor.close()
        conn.close()
        
        if hme_count == 0:
            print("  ⚠ No recent HME data found")
        if labor_count == 0:
            print("  ⚠ No recent Labor data found")
        if medallia_count == 0:
            print("  ⚠ No recent Medallia data found")
        
        print()
        return True
        
    except Exception as e:
        print(f"  ✗ Data check failed: {e}")
        print()
        return False


def main():
    """Run all tests."""
    print("🔍 Pardelta Dashboard Connection Troubleshooter")
    print("=" * 50)
    print()
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Secrets", test_secrets()))
    results.append(("Supabase API", test_supabase_api()))
    results.append(("PostgreSQL", test_postgresql()))
    results.append(("Data", test_data_availability()))
    
    print("=" * 50)
    print("📋 Summary:")
    print()
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {test_name}")
        if not passed:
            all_passed = False
    
    print()
    
    if all_passed:
        print("🎉 All tests passed! You're ready to run the dashboard.")
        print("   Run: streamlit run pardelta_dashboard.py")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("   Refer to README.md for setup instructions.")
    
    print()
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()