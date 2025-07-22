# Customer Sentiment Analysis System 🎤📊

A comprehensive audio-based customer sentiment analysis system that combines OpenAI's Whisper for speech transcription with advanced sentiment analysis to detect customer purchase intentions and emotional responses.

## Features ✨

- **🎵 Audio Transcription**: Uses OpenAI Whisper for accurate speech-to-text conversion
- **😊 Sentiment Analysis**: Analyzes emotional tone (positive/negative/neutral)
- **🛒 Purchase Intent Detection**: Identifies customer buying intentions with confidence scores
- **🎭 Emotional Analysis**: Detects specific emotions (excitement, satisfaction, frustration, etc.)
- **🔍 Key Phrase Extraction**: Identifies important phrases related to purchase intent
- **🌐 Web Interface**: Easy-to-use web interface for file upload and analysis
- **⚡ Command Line Interface**: Batch processing and automation support
- **📊 JSON Export**: Structured data export for further analysis
- **🎯 Multiple Models**: Support for different Whisper model sizes

## Quick Start 🚀

### 1. Installation

```bash
# Clone or download the project files
cd whisper

# Run the automated setup
python setup.py
```

### 2. Basic Usage

#### Web Interface (Recommended for beginners)
```bash
python web_interface.py
# Open http://localhost:5000 in your browser
```

#### Command Line Interface
```bash
# Analyze a single file
python cli_analyzer.py customer_call.wav

# Batch process a directory
python cli_analyzer.py --batch audio_files/

# Use different Whisper model
python cli_analyzer.py --model small.en audio.mp3
```

#### Python API
```python
from customer_sentiment_analyzer import CustomerSentimentAnalyzer

analyzer = CustomerSentimentAnalyzer()
result = analyzer.analyze_audio('audio_file.wav')
analyzer.print_analysis(result)
```

### 3. Try the Example
```bash
python example_usage.py
```

## Installation Details 📋

### Prerequisites
- Python 3.8 or higher
- ffmpeg (for audio processing)

### Install ffmpeg
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### Manual Installation
```bash
# Install Python dependencies
pip install -r requirements_extended.txt

# Download NLTK data (if needed)
python -c "import nltk; nltk.download('punkt'); nltk.download('vader_lexicon')"
```

## Supported Audio Formats 🎵

- WAV (recommended)
- MP3
- FLAC
- M4A
- OGG
- AAC

Maximum file size: 50MB (configurable)

## Analysis Output 📊

Each analysis provides:

### Transcription
- Complete text transcription of the audio
- Automatic language detection
- Word-level timestamps (optional)

### Sentiment Analysis
- Sentiment score (-1.0 to 1.0)
- Classification (Positive/Negative/Neutral)
- Confidence level

### Purchase Intent Detection
- Intent detection (Yes/No)
- Confidence score (0.0 to 1.0)
- Intent strength (High/Medium/Low)
- Key phrases that indicate purchase intent

### Emotional Analysis
- Excitement level
- Satisfaction indicators
- Frustration markers
- Uncertainty detection
- Enthusiasm measurement

## Example Analysis Result

```json
{
  "text": "I love this product! It's exactly what I was looking for. I definitely want to buy it.",
  "sentiment_score": 0.8,
  "confidence": 0.85,
  "purchase_intent": true,
  "purchase_confidence": 0.92,
  "key_phrases": ["want to buy", "exactly what I was looking for"],
  "emotions": {
    "excitement": 0.7,
    "satisfaction": 0.8,
    "enthusiasm": 0.9
  },
  "timestamp": "2024-01-20T15:30:45"
}
```

## Available Whisper Models 🤖

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| `tiny.en` | 39M | Fastest | Basic | Quick testing |
| `base.en` | 74M | Fast | Good | **Default choice** |
| `small.en` | 244M | Medium | Better | Higher accuracy needed |
| `medium.en` | 769M | Slow | Best | Maximum accuracy |

## Use Cases 📈

### Customer Service Analysis
- Analyze customer support calls
- Detect customer satisfaction levels
- Identify escalation risks
- Monitor service quality

### Sales Call Analysis
- Identify hot leads
- Track purchase intentions
- Analyze objections and concerns
- Optimize sales strategies

### Product Review Analysis
- Process video/audio reviews
- Extract sentiment trends
- Identify product issues
- Understand customer preferences

### Market Research
- Analyze focus group recordings
- Process customer interviews
- Extract insights from feedback
- Sentiment tracking over time

## API Reference 📚

### CustomerSentimentAnalyzer Class

```python
analyzer = CustomerSentimentAnalyzer(
    model_size="base.en",  # Whisper model size
    device="auto"          # "cpu", "cuda", "mps", or "auto"
)

# Main analysis method
result = analyzer.analyze_audio(
    audio_path="audio.wav",
    language="en"  # Optional: auto-detect if not specified
)

# Display results
analyzer.print_analysis(result)

# Save results to JSON
analyzer.save_result(result, "original_filename.wav")
```

### SentimentResult Object

```python
@dataclass
class SentimentResult:
    text: str                    # Transcribed text
    sentiment_score: float       # -1 (negative) to 1 (positive)
    confidence: float           # Confidence in sentiment
    purchase_intent: bool       # Purchase intent detected
    purchase_confidence: float  # Purchase intent confidence
    key_phrases: List[str]      # Key phrases for intent
    emotions: Dict[str, float]  # Emotional analysis
    timestamp: str              # Analysis timestamp
```

## Command Line Options ⌨️

```bash
python cli_analyzer.py [OPTIONS] AUDIO_FILES

Options:
  --model MODEL          Whisper model (default: base.en)
  --language LANG        Audio language (auto-detect if not specified)
  --output FILE          Save results to JSON file
  --batch               Process directories recursively
  --quiet               Show only summary output
  --help                Show help message

Examples:
  python cli_analyzer.py call.wav
  python cli_analyzer.py --model small.en --output results.json audio1.mp3 audio2.wav
  python cli_analyzer.py --batch --quiet audio_folder/
```

## Web Interface Features 🌐

- **Drag & Drop Upload**: Easy file upload
- **Real-time Analysis**: Instant processing and results
- **Visual Results**: Formatted output with color coding
- **Responsive Design**: Works on desktop and mobile
- **Error Handling**: Clear error messages and guidance

## File Structure 📁

```
whisper/
├── customer_sentiment_analyzer.py  # Main analyzer class
├── web_interface.py               # Flask web application
├── cli_analyzer.py               # Command line interface
├── example_usage.py              # Usage examples
├── setup.py                      # Automated setup script
├── requirements_extended.txt     # Python dependencies
├── templates/
│   └── index.html               # Web interface template
├── uploads/                     # Uploaded audio files
├── sentiment_results/          # Analysis results (JSON)
├── sample_audio/              # Sample audio files
└── logs/                      # Log files
```

## Configuration Options ⚙️

### Model Selection
Choose the appropriate Whisper model based on your needs:
- **Speed**: tiny.en > base.en > small.en > medium.en
- **Accuracy**: medium.en > small.en > base.en > tiny.en
- **Memory**: tiny.en < base.en < small.en < medium.en

### Purchase Intent Detection
Customize keywords and phrases in `customer_sentiment_analyzer.py`:
```python
self.purchase_positive_keywords = {
    'buy', 'purchase', 'order', 'interested', ...
}
self.purchase_negative_keywords = {
    'expensive', 'costly', 'bad', 'terrible', ...
}
```

## Performance Tips 💡

1. **Model Selection**: Use `base.en` for balanced speed/accuracy
2. **Audio Quality**: Higher quality audio = better transcription
3. **File Format**: WAV format typically works best
4. **File Size**: Keep files under 10MB for faster processing
5. **Batch Processing**: Use CLI for multiple files

## Troubleshooting 🔧

### Common Issues

**"ffmpeg not found"**
- Install ffmpeg using your system's package manager
- Ensure ffmpeg is in your PATH

**"No module named 'whisper'"**
- Run `python setup.py` to install dependencies
- Or manually: `pip install openai-whisper`

**"CUDA out of memory"**
- Use smaller Whisper model (`tiny.en` or `base.en`)
- Set device to "cpu": `CustomerSentimentAnalyzer(device="cpu")`

**"No speech detected"**
- Check audio quality and volume
- Ensure audio contains speech
- Try different audio format

### Performance Issues
- Use smaller model sizes for faster processing
- Process shorter audio clips (< 30 seconds) for speed
- Use GPU if available (CUDA/MPS)

## Development 👩‍💻

### Extending the Analyzer

```python
class CustomSentimentAnalyzer(CustomerSentimentAnalyzer):
    def analyze_custom_features(self, text):
        # Add custom analysis logic
        return custom_results
```

### Adding New Emotions
```python
def extract_emotions(self, text):
    emotions = super().extract_emotions(text)
    # Add custom emotion detection
    emotions['custom_emotion'] = self.detect_custom_emotion(text)
    return emotions
```

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License 📄

This project builds upon OpenAI's Whisper (MIT License) and includes additional components under MIT License.

## Support 💬

For issues and questions:
1. Check the troubleshooting section
2. Run `python setup.py` to verify installation
3. Test with `python example_usage.py`
4. Check log files in the `logs/` directory

## Changelog 📝

### v1.0.0
- Initial release
- Whisper integration
- Sentiment analysis
- Purchase intent detection
- Web and CLI interfaces
- Emotional analysis
- JSON export functionality

---

**Ready to analyze customer sentiment? Start with `python setup.py` and then try `python example_usage.py`!** 🎉
