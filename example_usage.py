"""
Example Usage of Customer Sentiment Analyzer

This script demonstrates how to use the sentiment analyzer with sample audio files.
"""

import os
import sys
from pathlib import Path
import tempfile
import wave
import numpy as np

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from customer_sentiment_analyzer import CustomerSentimentAnalyzer
    print("✅ Successfully imported CustomerSentimentAnalyzer")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nPlease install the required dependencies:")
    print("pip install -r requirements_extended.txt")
    sys.exit(1)


def create_sample_audio(text, filename, duration=3.0, sample_rate=22050):
    """
    Create a simple sine wave audio file (placeholder for actual speech).
    In real use, you would provide actual recorded audio files.
    """
    # Generate a simple sine wave
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    frequency = 440  # A4 note
    audio = np.sin(2 * np.pi * frequency * t) * 0.3
    
    # Convert to 16-bit integers
    audio = (audio * 32767).astype(np.int16)
    
    # Save as WAV file
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio.tobytes())
    
    print(f"Created sample audio file: {filename}")
    print(f"Note: This is a sine wave placeholder. Replace with actual speech recording for: '{text}'")


def main():
    """Demonstrate the sentiment analyzer with example scenarios."""
    
    print("🎤 Customer Sentiment Analyzer - Example Usage")
    print("=" * 60)
    
    # Initialize the analyzer
    print("\nInitializing sentiment analyzer...")
    try:
        analyzer = CustomerSentimentAnalyzer(model_size="base.en")
        print("✅ Analyzer initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize analyzer: {e}")
        return
    
    # Create sample directory
    sample_dir = Path("sample_audio")
    sample_dir.mkdir(exist_ok=True)
    
    # Example scenarios with different sentiment and purchase intent
    scenarios = [
        {
            "text": "I love this product! It's exactly what I was looking for. I definitely want to buy it.",
            "filename": "positive_purchase_intent.wav",
            "description": "Positive sentiment with clear purchase intent"
        },
        {
            "text": "This product seems okay, but I'm not sure if it's worth the price. Maybe I'll think about it.",
            "filename": "neutral_uncertain.wav", 
            "description": "Neutral sentiment with uncertain purchase intent"
        },
        {
            "text": "I hate this product! It's terrible and overpriced. I would never recommend it to anyone.",
            "filename": "negative_no_intent.wav",
            "description": "Negative sentiment with no purchase intent"
        },
        {
            "text": "The product looks great and has good reviews. How much does it cost? I'm interested in ordering.",
            "filename": "inquiry_purchase.wav",
            "description": "Positive sentiment with price inquiry and purchase interest"
        }
    ]
    
    print(f"\nCreating {len(scenarios)} sample audio files...")
    print("Note: These are placeholder sine waves. In real usage, provide actual speech recordings.\n")
    
    # Process each scenario
    for i, scenario in enumerate(scenarios, 1):
        print(f"[{i}/{len(scenarios)}] {scenario['description']}")
        print(f"Sample text: '{scenario['text']}'")
        
        # Create sample audio file
        audio_path = sample_dir / scenario['filename']
        create_sample_audio(scenario['text'], str(audio_path))
        
        print(f"📂 To test with real audio, replace {audio_path} with actual recording")
        print("-" * 40)
    
    print("\n🚀 How to use the analyzer:")
    print("\n1. Replace sample files with real audio recordings")
    print("2. Use the command line interface:")
    print("   python cli_analyzer.py sample_audio/positive_purchase_intent.wav")
    print("\n3. Use the web interface:")
    print("   python web_interface.py")
    print("   Then open http://localhost:5000 in your browser")
    print("\n4. Use programmatically:")
    print("""
   from customer_sentiment_analyzer import CustomerSentimentAnalyzer
   
   analyzer = CustomerSentimentAnalyzer()
   result = analyzer.analyze_audio('your_audio_file.wav')
   analyzer.print_analysis(result)
    """)
    
    # Example of programmatic usage if user wants to test with actual audio
    print("\n5. Test with existing audio files (if available):")
    test_files = list(Path(".").glob("*.wav")) + list(Path(".").glob("*.mp3"))
    
    if test_files:
        print("   Found audio files in current directory:")
        for file in test_files[:3]:  # Show first 3 files
            print(f"   - {file}")
        
        # Ask if user wants to test with one of them
        print(f"\n   To analyze {test_files[0]}:")
        print(f"   python cli_analyzer.py {test_files[0]}")
    else:
        print("   No existing audio files found in current directory")
    
    print("\n📋 Available Whisper Models:")
    models = ["tiny.en", "base.en", "small.en", "medium.en"]
    for model in models:
        print(f"   - {model}")
    
    print("\n📊 Analysis Features:")
    features = [
        "Speech-to-text transcription using OpenAI Whisper",
        "Sentiment analysis (positive/negative/neutral)",
        "Purchase intention detection with confidence scores",
        "Emotional analysis (excitement, satisfaction, frustration, etc.)",
        "Key phrase extraction for purchase intent",
        "Web interface for easy file upload and analysis",
        "Command-line interface for batch processing",
        "JSON export of analysis results"
    ]
    
    for feature in features:
        print(f"   ✓ {feature}")
    
    print(f"\n📁 Sample files created in: {sample_dir.absolute()}")
    print("Replace these with actual customer audio recordings for real analysis!")


if __name__ == "__main__":
    main()
