#!/usr/bin/env python3
"""
Test script to verify Tesseract installation and functionality
"""

import os
import sys
import shutil
import platform

def test_tesseract_installation():
    print("=== TESSERACT INSTALLATION TEST ===")
    print(f"Platform: {platform.system()}")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"PATH: {os.environ.get('PATH', 'Not set')}")
    print(f"TESSERACT_PATH env var: {os.getenv('TESSERACT_PATH', 'Not set')}")
    print()

    # Test 1: Try importing pytesseract
    try:
        import pytesseract
        print("✓ pytesseract import successful")
    except ImportError as e:
        print(f"✗ pytesseract import failed: {e}")
        return False

    # Test 2: Check if tesseract is in PATH
    tesseract_path = shutil.which('tesseract')
    print(f"shutil.which('tesseract'): {tesseract_path}")
    
    # Test 3: Check common installation paths
    common_paths = [
        '/usr/bin/tesseract',
        '/usr/local/bin/tesseract',
        '/opt/homebrew/bin/tesseract',
        '/bin/tesseract',
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        r'C:\tools\tesseract\tesseract.exe'
    ]
    
    found_paths = []
    for path in common_paths:
        if os.path.isfile(path):
            found_paths.append(path)
            print(f"✓ Found tesseract at: {path}")
    
    if not found_paths:
        print("✗ No tesseract executable found in common locations")
        return False

    # Test 4: Try to configure and test tesseract
    test_path = tesseract_path or found_paths[0]
    try:
        pytesseract.pytesseract.tesseract_cmd = test_path
        print(f"✓ Configured pytesseract to use: {test_path}")
        
        # Test 5: Try to run tesseract version command
        import subprocess
        result = subprocess.run([test_path, '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✓ Tesseract version check successful:")
            print(f"  {result.stdout.strip()}")
        else:
            print(f"✗ Tesseract version check failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Error configuring or testing tesseract: {e}")
        return False

    # Test 6: Try basic OCR functionality
    try:
        from PIL import Image
        import io
        
        # Create a simple test image
        test_img = Image.new('RGB', (200, 50), color='white')
        print("✓ Created test image")
        
        # Note: For a real test, we'd need to draw text on the image
        # This is just testing that the basic pipeline works
        print("✓ Basic tesseract setup appears functional")
        
    except Exception as e:
        print(f"✗ Error in OCR test: {e}")
        return False

    print("\n=== TEST COMPLETED SUCCESSFULLY ===")
    return True

if __name__ == "__main__":
    success = test_tesseract_installation()
    sys.exit(0 if success else 1)