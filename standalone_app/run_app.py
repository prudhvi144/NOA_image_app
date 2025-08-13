#!/usr/bin/env python3
"""
Simple launcher script for the Sperm Verification App.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from sperm_verification_app import main
    
    if __name__ == "__main__":
        sys.exit(main())
        
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please ensure all dependencies are installed:")
    print("pip install -r requirements.txt")
    sys.exit(1)
