"""
Dependency Checker for Gmail Add-on
Checks if all required dependencies are installed.
"""

import sys

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("="*60)
    print("Gmail Add-on Dependency Checker")
    print("="*60)
    
    required_modules = {
        'numpy': 'Core numerical library',
        'pandas': 'Data manipulation',
        'nltk': 'Natural Language Processing',
        'beautifulsoup4': 'HTML parsing',
        'sklearn': 'Machine Learning (scikit-learn)',
        'joblib': 'Model serialization (optional)',
    }
    
    missing = []
    installed = []
    
    print("\nChecking dependencies...")
    print("-" * 60)
    
    for module_name, description in required_modules.items():
        # Handle special cases
        import_name = module_name
        if module_name == 'beautifulsoup4':
            import_name = 'bs4'
        elif module_name == 'sklearn':
            import_name = 'sklearn'
        
        try:
            __import__(import_name)
            print(f"✓ {module_name:20} - {description}")
            installed.append(module_name)
        except ImportError:
            if module_name == 'joblib':
                print(f"ℹ {module_name:20} - {description} (optional, will use rule-based detection)")
            else:
                print(f"✗ {module_name:20} - {description} (MISSING)")
                missing.append(module_name)
    
    print("-" * 60)
    
    if missing:
        print(f"\n❌ Missing {len(missing)} required dependencies!")
        print("\nTo install missing dependencies, run:")
        print(f"  pip3 install {' '.join(missing)}")
        print("\nOr install all dependencies:")
        print("  pip3 install -r requirements.txt")
        return False
    else:
        print("\n✅ All required dependencies are installed!")
        print("\nYou can now:")
        print("  1. Run tests: python3 test_addon.py")
        print("  2. Run demo: python3 demo_gmail_addon.py")
        print("  3. Start integrating the add-on")
        return True

if __name__ == '__main__':
    success = check_dependencies()
    sys.exit(0 if success else 1)
