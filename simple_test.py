"""
Simple Connection Test for Pardelta Dashboard
"""

print("=" * 60)
print("PARDELTA DASHBOARD - CONNECTION TEST")
print("=" * 60)
print()

# Test 1: Check Python packages
print("Step 1: Testing Python packages...")
try:
    import streamlit
    print("  ✓ streamlit installed")
except ImportError as e:
    print(f"  ✗ streamlit not installed: {e}")

try:
    import pandas
    print("  ✓ pandas installed")
except ImportError as e:
    print(f"  ✗ pandas not installed: {e}")

try:
    import supabase
    print("  ✓ supabase installed")
except ImportError as e:
    print(f"  ✗ supabase not installed: {e}")

try:
    import psycopg2
    print("  ✓ psycopg2 installed")
except ImportError as e:
    print(f"  ✗ psycopg2 not installed: {e}")

print()

# Test 2: Check if secrets file exists
print("Step 2: Checking secrets file...")
import os
from pathlib import Path

secrets_path = Path(".streamlit/secrets.toml")
if secrets_path.exists():
    print(f"  ✓ secrets.toml found at {secrets_path.absolute()}")
    
    # Read and check content
    content = secrets_path.read_text()
    print(f"  File size: {len(content)} bytes")
    
    if "your-project" in content or "YOUR_" in content:
        print("  ⚠ WARNING: File still contains template placeholder values")
        print("  → You need to replace placeholders with actual Supabase credentials")
    else:
        print("  ✓ File appears to have real configuration")
    
    # Show what's configured
    if "[supabase]" in content:
        print("  ✓ PostgreSQL config section found")
    if "supabase_url" in content:
        print("  ✓ API config found")
        
else:
    print(f"  ✗ secrets.toml NOT FOUND at {secrets_path.absolute()}")
    print("  → Create it from the template")

print()

# Test 3: Try to read secrets using streamlit
print("Step 3: Testing Streamlit secrets access...")
try:
    import streamlit as st
    
    # Try to access secrets
    try:
        secrets = st.secrets
        print("  ✓ Streamlit can read secrets")
        
        # Check what's configured
        has_url = bool(secrets.get("supabase_url"))
        has_key = bool(secrets.get("supabase_anon_key"))
        has_supabase_section = "supabase" in secrets
        
        if has_url and has_key:
            url = secrets.get("supabase_url", "")
            if "your-project" in url:
                print("  ⚠ API config has template values")
            else:
                print("  ✓ API credentials configured")
        
        if has_supabase_section:
            supabase_config = secrets.get("supabase", {})
            host = supabase_config.get("host", "")
            if "YOUR_" in host or not host:
                print("  ⚠ PostgreSQL config has template/empty values")
            else:
                print(f"  ✓ PostgreSQL configured (host: {host[:20]}...)")
                
    except Exception as e:
        print(f"  ✗ Error reading secrets: {e}")
        
except Exception as e:
    print(f"  ✗ Error with Streamlit: {e}")

print()

# Test 4: Try PostgreSQL connection
print("Step 4: Testing PostgreSQL connection...")
try:
    import streamlit as st
    import psycopg2
    
    supabase_config = st.secrets.get("supabase", {})
    host = supabase_config.get("host", "")
    database = supabase_config.get("database", "") or supabase_config.get("dbname", "")
    user = supabase_config.get("user", "")
    password = supabase_config.get("password", "")
    port = supabase_config.get("port", 5432)
    
    if not all([host, database, user, password]):
        print("  ⚠ PostgreSQL config incomplete")
        print(f"    host: {'✓' if host else '✗'}")
        print(f"    database: {'✓' if database else '✗'}")
        print(f"    user: {'✓' if user else '✗'}")
        print(f"    password: {'✓' if password else '✗'}")
    else:
        print(f"  Attempting connection to {host}...")
        try:
            conn = psycopg2.connect(
                host=host,
                database=database,
                user=user,
                password=password,
                port=port
            )
            print("  ✓ PostgreSQL connection successful!")
            
            # Test query
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM hme_report")
            count = cursor.fetchone()[0]
            print(f"  ✓ Database accessible ({count} HME records)")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"  ✗ Connection failed: {e}")
            
except Exception as e:
    print(f"  ✗ Error: {e}")

print()
print("=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print()
print("Next steps:")
print("1. Fix any issues shown above")
print("2. Update .streamlit/secrets.toml with real Supabase credentials")
print("3. Run: streamlit run app.py")
print()