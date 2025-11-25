#!/usr/bin/env python
"""
Setup script for Skill Taxonomy Pipeline
Installs dependencies and prepares the environment
"""
import subprocess
import sys
import os
from pathlib import Path


def setup_environment():
    """Setup the environment for the pipeline"""
    
    print("="*60)
    print("SKILL TAXONOMY PIPELINE - SETUP")
    print("="*60)
    
    # 1. Check Python version
    print("\n1. Checking Python version...")
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("   ✗ Python 3.8+ required")
        sys.exit(1)
    print(f"   ✓ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 2. Create virtual environment (optional)
    print("\n2. Virtual environment setup...")
    response = input("   Create virtual environment? (y/n): ").lower()
    if response == 'y':
        subprocess.run([sys.executable, "-m", "venv", "venv"])
        print("   ✓ Virtual environment created")
        print("   Activate it with: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)")
        print("   Then run this script again to continue setup")
        return
    
    # 3. Install dependencies
    print("\n3. Installing dependencies...")
    print("   This may take a few minutes...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("   ✓ Dependencies installed")
    except subprocess.CalledProcessError:
        print("   ✗ Failed to install dependencies")
        print("   Try: pip install -r requirements.txt manually")
        sys.exit(1)
    
    # 4. Download spaCy language model
    print("\n4. Downloading spaCy language model...")
    try:
        subprocess.run([
            sys.executable, "-m", "spacy", "download", "en_core_web_sm"
        ], check=True)
        print("   ✓ spaCy model downloaded")
    except:
        print("   ⚠ spaCy model download failed (optional)")
    
    # 5. Create necessary directories
    print("\n5. Creating project directories...")
    directories = [
        "data",
        "output", 
        "cache",
        "cache/embeddings",
        "cache/clustering",
        "cache/llm_cache"
    ]
    
    for dir_name in directories:
        Path(dir_name).mkdir(parents=True, exist_ok=True)
    print("   ✓ Directories created")
    
    # 6. Environment variables
    print("\n6. Environment variables setup...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("   Creating .env file...")
        
        api_key = input("   Enter OpenAI API key (optional, press Enter to skip): ").strip()
        
        with open(".env", "w") as f:
            f.write("# Environment variables for Skill Taxonomy Pipeline\n")
            f.write(f"OPENAI_API_KEY={api_key}\n")
            f.write("CUDA_AVAILABLE=0  # Set to 1 if you have GPU\n")
        
        print("   ✓ .env file created")
    else:
        print("   ✓ .env file already exists")
    
    # 7. Test imports
    print("\n7. Testing imports...")
    try:
        import pandas
        import numpy
        import sentence_transformers
        import hdbscan
        import umap
        print("   ✓ Core packages imported successfully")
    except ImportError as e:
        print(f"   ✗ Import error: {e}")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Prepare your skills data as a CSV or DataFrame")
    print("2. Run: python example_usage.py (for demo)")
    print("3. Or run: python main.py your_skills.csv -o output_dir")
    

if __name__ == "__main__":
    setup_environment()
