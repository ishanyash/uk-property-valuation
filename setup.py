#!/usr/bin/env python3
"""
Property Valuation AI - Setup Script
=====================================

This script helps you set up the Property Valuation AI application.
It will check dependencies, create necessary directories, and guide you through the setup process.
"""

import os
import sys
import subprocess
import importlib.util

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    print("🐍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required. You have Python {}.{}.{}".format(
            sys.version_info.major, sys.version_info.minor, sys.version_info.micro))
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} is supported")
    return True

def check_package(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        return True
    except ImportError:
        return False

def install_package(package_name):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        return False

def check_and_install_dependencies():
    """Check and install required dependencies"""
    print("\n📦 Checking dependencies...")
    
    dependencies = [
        ("flask", "flask"),
        ("fpdf2", "fpdf"),
        ("python-dotenv", "dotenv"),
        ("openai", "openai"),
        ("requests", "requests"),
        ("beautifulsoup4", "bs4")
    ]
    
    missing_packages = []
    
    for package_name, import_name in dependencies:
        if check_package(package_name, import_name):
            print(f"✅ {package_name} is installed")
        else:
            print(f"❌ {package_name} is missing")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\n🔧 Installing missing packages: {', '.join(missing_packages)}")
        for package in missing_packages:
            print(f"Installing {package}...")
            if install_package(package):
                print(f"✅ {package} installed successfully")
            else:
                print(f"❌ Failed to install {package}")
                return False
    
    return True

def create_env_file():
    """Create a .env file if it doesn't exist"""
    print("\n⚙️ Setting up environment file...")
    
    if os.path.exists('.env'):
        print("✅ .env file already exists")
        return True
    
    env_content = """# OpenAI API Configuration
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# Flask Configuration
FLASK_SECRET_KEY=your_secret_key_here

# Optional: OpenAI API Base URL (leave default unless using custom endpoint)
# OPENAI_API_BASE=https://api.openai.com/v1
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")
        print("📝 Please edit .env file and add your OpenAI API key")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def check_required_files():
    """Check if all required files are present"""
    print("\n📁 Checking required files...")
    
    required_files = [
        'test.py',
        'app.py'  # This will be the new Flask app we created
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} found")
        else:
            print(f"❌ {file} missing")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n⚠️ Missing files: {', '.join(missing_files)}")
        print("Please ensure all required files are in the current directory")
        return False
    
    return True

def test_openai_connection():
    """Test OpenAI API connection"""
    print("\n🔑 Testing OpenAI API connection...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your_openai_api_key_here':
            print("⚠️ OpenAI API key not set in .env file")
            print("Please edit .env file and add your API key, then run this script again")
            return False
        
        import openai
        client = openai.OpenAI(api_key=api_key)
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello, this is a test."}],
            max_tokens=10
        )
        
        print("✅ OpenAI API connection successful")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API connection failed: {e}")
        print("Please check your API key and internet connection")
        return False

def create_run_script():
    """Create a simple run script"""
    print("\n📝 Creating run script...")
    
    run_script_content = """#!/usr/bin/env python3
\"\"\"
Property Valuation AI - Run Script
\"\"\"

import os
import sys

def main():
    print("🏠 Starting Property Valuation AI...")
    print("📊 Open your browser and go to: http://localhost:8000")
    print("🔑 Make sure to enter your OpenAI API key in the interface")
    print("📍 Example address: 381 Filton Avenue, BS7 0LH")
    print("=" * 50)
    
    try:
        from app import app
        app.run(host='0.0.0.0', port=8000, debug=False)
    except ImportError as e:
        print(f"❌ Error importing app: {e}")
        print("Please make sure all dependencies are installed")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
"""
    
    try:
        with open('run.py', 'w') as f:
            f.write(run_script_content)
        
        # Make it executable on Unix-like systems
        if os.name != 'nt':
            os.chmod('run.py', 0o755)
        
        print("✅ Created run.py script")
        return True
    except Exception as e:
        print(f"❌ Failed to create run script: {e}")
        return False

def print_instructions():
    """Print final setup instructions"""
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETE!")
    print("=" * 60)
    print()
    print("📋 Next Steps:")
    print("1. Edit the .env file and add your OpenAI API key")
    print("   Get your key from: https://platform.openai.com/api-keys")
    print()
    print("2. Run the application:")
    print("   python run.py")
    print("   OR")
    print("   python app.py")
    print()
    print("3. Open your browser and go to:")
    print("   http://localhost:8000")
    print()
    print("4. Enter your OpenAI API key in the interface")
    print()
    print("5. Try with example address:")
    print("   381 Filton Avenue, BS7 0LH")
    print()
    print("=" * 60)
    print("🚀 Happy property analyzing!")
    print("=" * 60)

def main():
    """Main setup function"""
    print("🏠 Property Valuation AI - Setup Script")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check and install dependencies
    if not check_and_install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        print("❌ Failed to create .env file")
        sys.exit(1)
    
    # Check required files
    if not check_required_files():
        print("❌ Missing required files")
        sys.exit(1)
    
    # Create run script
    if not create_run_script():
        print("❌ Failed to create run script")
        sys.exit(1)
    
    # Test OpenAI connection (optional)
    print("\n🧪 Would you like to test the OpenAI API connection now?")
    test_choice = input("Enter 'y' to test, or any other key to skip: ").lower()
    if test_choice == 'y':
        if not test_openai_connection():
            print("⚠️ API test failed, but you can still run the app and enter your key in the interface")
    
    # Print final instructions
    print_instructions()

if __name__ == '__main__':
    main()