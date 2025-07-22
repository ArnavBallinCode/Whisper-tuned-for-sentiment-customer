#!/usr/bin/env python3
"""
Setup script for Customer Sentiment Analysis System

This script installs all required dependencies and sets up the environment.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(
            command.split(),
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ {description} failed: {str(e)}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major != 3 or version.minor < 8:
        print(f"❌ Python 3.8+ is required. Current version: {version.major}.{version.minor}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True


def check_ffmpeg():
    """Check if ffmpeg is installed."""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ffmpeg is installed")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ ffmpeg is not installed")
    print("   Please install ffmpeg:")
    print("   - macOS: brew install ffmpeg")
    print("   - Ubuntu: sudo apt update && sudo apt install ffmpeg")
    print("   - Windows: Download from https://ffmpeg.org/download.html")
    return False


def install_dependencies():
    """Install Python dependencies."""
    requirements_file = Path("requirements_extended.txt")
    
    if not requirements_file.exists():
        print(f"❌ Requirements file not found: {requirements_file}")
        return False
    
    # Install core dependencies first
    core_deps = [
        "torch",
        "numpy", 
        "whisper",
        "textblob",
        "flask",
        "librosa"
    ]
    
    print("📦 Installing core dependencies...")
    for dep in core_deps:
        if not run_command(f"{sys.executable} -m pip install {dep}", f"Installing {dep}"):
            print(f"⚠️  Failed to install {dep}, but continuing...")
    
    # Install all requirements
    cmd = f"{sys.executable} -m pip install -r {requirements_file}"
    return run_command(cmd, "Installing all dependencies from requirements_extended.txt")


def download_nltk_data():
    """Download required NLTK data."""
    print("📦 Downloading NLTK data...")
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('vader_lexicon', quiet=True)
        nltk.download('brown', quiet=True)
        print("✅ NLTK data downloaded")
        return True
    except Exception as e:
        print(f"⚠️  Failed to download NLTK data: {e}")
        return False


def create_directories():
    """Create necessary directories."""
    directories = [
        "uploads",
        "sentiment_results", 
        "sample_audio",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Created directory: {directory}")
    
    return True


def test_installation():
    """Test if the installation works."""
    print("\n🧪 Testing installation...")
    
    try:
        # Test Whisper
        import whisper
        print("✅ Whisper imported successfully")
        
        # Test TextBlob
        from textblob import TextBlob
        blob = TextBlob("This is a test.")
        sentiment = blob.sentiment.polarity
        print("✅ TextBlob working correctly")
        
        # Test Flask
        from flask import Flask
        print("✅ Flask imported successfully")
        
        # Test our main analyzer
        from customer_sentiment_analyzer import CustomerSentimentAnalyzer
        print("✅ CustomerSentimentAnalyzer imported successfully")
        
        print("✅ All components are working!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def print_usage_instructions():
    """Print usage instructions."""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    
    print("\n🚀 How to use your Customer Sentiment Analyzer:")
    
    print("\n1️⃣  Command Line Interface:")
    print("   python cli_analyzer.py your_audio_file.wav")
    print("   python cli_analyzer.py --batch audio_folder/")
    print("   python cli_analyzer.py --help  # for more options")
    
    print("\n2️⃣  Web Interface:")
    print("   python web_interface.py")
    print("   Then open http://localhost:5000 in your browser")
    
    print("\n3️⃣  Python API:")
    print("""   from customer_sentiment_analyzer import CustomerSentimentAnalyzer
   
   analyzer = CustomerSentimentAnalyzer()
   result = analyzer.analyze_audio('audio.wav')
   analyzer.print_analysis(result)""")
    
    print("\n4️⃣  Example Usage:")
    print("   python example_usage.py  # Creates sample files and shows examples")
    
    print("\n📋 Supported Audio Formats:")
    print("   WAV, MP3, FLAC, M4A, OGG, AAC")
    
    print("\n📊 Analysis Features:")
    print("   ✓ Speech transcription using OpenAI Whisper")
    print("   ✓ Sentiment analysis (positive/negative/neutral)")
    print("   ✓ Purchase intention detection")
    print("   ✓ Emotional analysis")
    print("   ✓ Key phrase extraction")
    print("   ✓ Confidence scoring")
    print("   ✓ JSON export of results")
    
    print("\n📁 File Structure:")
    print("   uploads/           - Uploaded audio files")
    print("   sentiment_results/ - Analysis results (JSON)")
    print("   sample_audio/      - Sample audio files")
    print("   logs/              - Log files")
    
    print("\n📚 Next Steps:")
    print("   1. Try the example: python example_usage.py")
    print("   2. Upload your audio files for analysis")
    print("   3. Check the sentiment_results/ folder for saved analyses")
    
    print("\n" + "="*60)


def main():
    """Main setup function."""
    print("🎤 Customer Sentiment Analyzer Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check ffmpeg
    ffmpeg_ok = check_ffmpeg()
    if not ffmpeg_ok:
        print("\n⚠️  Continue anyway? ffmpeg is needed for audio processing.")
        response = input("Continue setup? (y/n): ").lower().strip()
        if response != 'y':
            print("Setup cancelled. Please install ffmpeg first.")
            sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Download NLTK data
    download_nltk_data()
    
    # Create directories
    create_directories()
    
    # Test installation
    if not test_installation():
        print("❌ Installation test failed")
        sys.exit(1)
    
    # Print usage instructions
    print_usage_instructions()


if __name__ == "__main__":
    main()
