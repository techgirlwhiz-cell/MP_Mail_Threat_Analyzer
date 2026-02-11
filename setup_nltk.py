"""
Setup script to download required NLTK data.
Run this once before using the phishing detection system.
"""

import nltk

def download_nltk_resources():
    """Download all required NLTK resources."""
    print("Downloading NLTK resources...")
    print("This may take a few moments...")
    
    resources = ['punkt', 'punkt_tab', 'stopwords']
    
    for resource in resources:
        try:
            print(f"Downloading {resource}...", end=' ')
            nltk.download(resource, quiet=False)
            print("✓")
        except Exception as e:
            print(f"✗ Error: {e}")
            print(f"  You may need to download {resource} manually.")
    
    print("\nNLTK setup complete!")
    print("\nTo verify, try running: python quick_test.py")

if __name__ == '__main__':
    download_nltk_resources()

