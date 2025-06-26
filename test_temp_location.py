#!/usr/bin/env python3
"""
Test script to show where temporary invoice files will be created
"""
import os
import tempfile
from pathlib import Path

# Simulate Django settings.BASE_DIR
BASE_DIR = Path(__file__).resolve().parent

def test_temp_locations():
    print("🔍 Testing Temporary File Locations:")
    print("=" * 50)
    
    # Show default system temp location
    default_temp = tempfile.gettempdir()
    print(f"1. System Default Temp: {default_temp}")
    
    # Test system temp directory creation
    try:
        system_temp_dir = tempfile.mkdtemp()
        print(f"   ✅ System temp works: {system_temp_dir}")
        os.rmdir(system_temp_dir)
    except Exception as e:
        print(f"   ❌ System temp failed: {e}")
    
    # Show project temp location (what we'll use now)
    project_temp_base = os.path.join(BASE_DIR, 'temp_invoices')
    print(f"\n2. Project Temp Base: {project_temp_base}")
    
    # Test project temp directory creation
    try:
        os.makedirs(project_temp_base, exist_ok=True)
        project_temp_dir = tempfile.mkdtemp(dir=project_temp_base)
        print(f"   ✅ Project temp works: {project_temp_dir}")
        
        # Test HTML file creation
        html_temp = tempfile.NamedTemporaryFile(
            suffix='.html', 
            delete=False, 
            dir=project_temp_dir
        )
        html_temp.close()
        print(f"   ✅ HTML temp file: {html_temp.name}")
        
        # Cleanup
        os.unlink(html_temp.name)
        os.rmdir(project_temp_dir)
        
    except Exception as e:
        print(f"   ❌ Project temp failed: {e}")
    
    print("\n📋 Summary:")
    print("- OLD: Files created in system temp (may not work on live server)")
    print("- NEW: Files created in project/temp_invoices/ (should work everywhere)")
    print("\n🚀 Now your live server will create files like:")
    print(f"   {project_temp_base}/tmp[random]/invoice_INV-00001.png")

if __name__ == "__main__":
    test_temp_locations() 