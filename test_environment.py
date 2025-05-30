#!/usr/bin/env python3
"""
Environment Test Script
Check if all packages are properly installed in the current environment
"""

import sys
import os

def test_package_import(package_name, import_name=None):
    """Test if a package can be imported"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✅ {package_name} - OK")
        return True
    except ImportError as e:
        print(f"❌ {package_name} - FAILED: {e}")
        return False

def main():
    print("🧪 Environment Test Script")
    print("=" * 40)
    print(f"🐍 Python version: {sys.version}")
    print(f"📍 Python location: {sys.executable}")
    print(f"📁 Current directory: {os.getcwd()}")
    print()
    
    print("📦 Testing package imports:")
    print("-" * 30)
    
    packages = [
        ("flask", "flask"),
        ("fpdf2", "fpdf"),
        ("python-dotenv", "dotenv"),
        ("openai", "openai"),
        ("requests", "requests"),
        ("beautifulsoup4", "bs4")
    ]
    
    all_ok = True
    failed_packages = []
    
    for package_name, import_name in packages:
        if not test_package_import(package_name, import_name):
            all_ok = False
            failed_packages.append(package_name)
    
    print()
    if all_ok:
        print("🎉 All packages are installed correctly!")
        print("✅ You're ready to run the Property Valuation AI app!")
    else:
        print("❌ Some packages are missing or not installed correctly")
        print()
        print("🔧 To fix missing packages, run:")
        for pkg in failed_packages:
            if pkg == "openai":
                print(f"  pip install {pkg}")
            else:
                print(f"  conda install -c conda-forge {pkg}")
        print()
        print("💡 Or install all at once:")
        print("  conda install -c conda-forge flask python-dotenv requests beautifulsoup4 fpdf2")
        print("  pip install openai")
    
    print()
    print("🌍 Environment Information:")
    print("-" * 30)
    
    # Check if we're in a conda environment
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    if conda_env:
        print(f"🔹 Conda environment: {conda_env}")
    else:
        print("🔹 Not in a conda environment")
    
    # Check conda prefix
    conda_prefix = os.environ.get('CONDA_PREFIX')
    if conda_prefix:
        print(f"🔹 Conda prefix: {conda_prefix}")
    
    # Check if we can find conda
    try:
        import subprocess
        result = subprocess.run(['conda', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"🔹 Conda version: {result.stdout.strip()}")
    except:
        print("🔹 Conda not found in PATH")

if __name__ == '__main__':
    main()