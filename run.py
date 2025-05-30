#!/usr/bin/env python3
"""
Property Valuation AI - Run Script
"""

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
