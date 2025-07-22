"""
Customer Sentiment Analyzer for Purchase Intention Detection

This module combines Whisper for audio transcription with sentiment analysis
to detect customer purchase intentions from audio recordings.
"""

import os
import json
import re
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import whisper
from textblob import TextBlob
import torch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class SentimentResult:
    """Data class for sentiment analysis results."""
    text: str
    sentiment_score: float  # -1 (negative) to 1 (positive)
    confidence: float
    purchase_intent: bool
    purchase_confidence: float
    key_phrases: List[str]
    emotions: Dict[str, float]
    timestamp: str


class CustomerSentimentAnalyzer:
    """
    A comprehensive sentiment analyzer that processes audio files to detect
    customer purchase intentions and overall sentiment.
    """
    
    def __init__(self, model_size: str = "large", device: str = "auto", default_language: str = "hi"):
        """
        Initialize the sentiment analyzer.
        
        Args:
            model_size: Whisper model size ("tiny", "base", "small", "medium", "large")
            device: Device to run on ("cpu", "cuda", or "auto")
            default_language: Language code for transcription (e.g., "hi" for Hindi)
        """
        self.model_size = model_size
        self.device = self._setup_device(device)
        self.default_language = default_language
        
        # Load Whisper model
        logger.info(f"Loading Whisper model: {model_size}")
        self.whisper_model = whisper.load_model(model_size, device=self.device)
        
        # Purchase intent keywords and phrases
        # English and Hindi purchase intent keywords
        self.purchase_positive_keywords = {
            # English
            'buy', 'purchase', 'order', 'get', 'want', 'need', 'interested',
            'like', 'love', 'perfect', 'excellent', 'great', 'amazing',
            'checkout', 'cart', 'payment', 'price', 'cost', 'afford',
            'deal', 'discount', 'offer', 'sale', 'recommend', 'approve',
            # Hindi (Devanagari)
            'खरीद', 'खरीदना', 'ऑर्डर', 'लेना', 'चाहता', 'चाहती', 'चाहिए', 'जरूरत',
            'पसंद', 'प्रेम', 'उत्तम', 'शानदार', 'अद्भुत', 'सही', 'बढ़िया', 'डील',
            'छूट', 'ऑफर', 'सिफारिश', 'मंजूर', 'कार्ट', 'भुगतान', 'कीमत', 'मूल्य', 'सस्ता',
            # Romanized Hindi
            'kharid', 'kharidna', 'order', 'lena', 'chahta', 'chahti', 'chahiye', 'zarurat',
            'pasand', 'prem', 'uttam', 'shandar', 'adbhut', 'sahi', 'badhiya', 'deal',
            'chhoot', 'offer', 'sifarish', 'manzoor', 'cart', 'bhugtan', 'keemat', 'moolya', 'sasta',
            # Hinglish (common mix)
            'i want to kharid', 'i want to buy', 'main kharidna chahta hoon', 'main kharidna chahti hoon',
            'order karna hai', 'cart mein daal do', 'payment karna hai', 'deal chahiye', 'offer chahiye',
            'price kitna hai', 'discount milega', 'checkout karna hai', 'yeh pasand hai', 'yeh perfect hai',
            'bahut accha hai', 'bahut badhiya hai', 'amazing lag raha hai', 'great deal', 'best price',
            'recommend karunga', 'recommend karungi', 'approve karta hoon', 'approve karti hoon'
        }

        self.purchase_negative_keywords = {
            # English
            'expensive', 'costly', 'cheap', 'poor', 'bad', 'terrible',
            'hate', 'dislike', 'cancel', 'return', 'refund', 'complaint',
            'problem', 'issue', 'broken', 'defective', 'disappointed',
            # Hindi (Devanagari)
            'महंगा', 'महंगी', 'सस्ता', 'सस्ती', 'खराब', 'बुरा', 'बेकार', 'नापसंद',
            'रद्द', 'वापसी', 'शिकायत', 'समस्या', 'टूटा', 'खराबी', 'निराश', 'गलत',
            # Romanized Hindi
            'mahanga', 'mahangi', 'sasta', 'sasti', 'kharab', 'bura', 'bekar', 'napasand',
            'radd', 'wapasi', 'shikayat', 'samasya', 'toota', 'kharabi', 'niraash', 'galat',
            # Hinglish (common mix)
            'yeh bahut mehenga hai', 'yeh pasand nahi', 'main cancel karna chahta hoon', 'main cancel karna chahti hoon',
            'refund chahiye', 'return karna hai', 'problem hai', 'issue hai', 'broken hai', 'defective piece',
            'disappointed hoon', 'niraash hoon', 'bekar lag raha hai', 'bad experience', 'complaint karunga', 'complaint karungi'
        }

        # Intent phrases patterns (English + Hindi)
        self.intent_patterns = [
            # English
            r'(?i)(?:want to|going to|planning to|thinking about)\s+(?:buy|purchase|get|order)',
            r'(?i)(?:interested in|looking for|searching for|need)\s+(?:this|that|it)',
            r'(?i)(?:how much|what.s the price|cost|pricing)',
            r'(?i)(?:add to cart|checkout|place order|make purchase)',
            r'(?i)(?:sounds good|looks great|perfect|exactly what)',
            r'(?i)(?:i.ll take it|sign me up|count me in)',
            # Hindi (Devanagari)
            r'(?:खरीदना चाहता|खरीदना चाहती|ऑर्डर करना|लेना है|चाहिए|जरूरत है)',
            r'(?:पसंद है|प्रेम है|उत्तम है|शानदार है|अद्भुत है|सही है|बढ़िया है)',
            r'(?:कीमत क्या है|मूल्य क्या है|सस्ता है|महंगा है|डील चाहिए|छूट चाहिए)',
            r'(?:कार्ट में डालो|भुगतान करो|ऑफर चाहिए|सिफारिश करो|मंजूर है)',
            # Romanized Hindi
            r'(?:kharidna chahta|kharidna chahti|order karna|lena hai|chahiye|zarurat hai)',
            r'(?:pasand hai|prem hai|uttam hai|shandar hai|adbhut hai|sahi hai|badhiya hai)',
            r'(?:keemat kya hai|moolya kya hai|sasta hai|mahanga hai|deal chahiye|chhoot chahiye)',
            r'(?:cart mein dalo|bhugtan karo|offer chahiye|sifarish karo|manzoor hai)',
            # Hinglish (common mix)
            r'(?:i want to kharid|main kharidna chahta hoon|main kharidna chahti hoon|order karna hai|cart mein daal do|payment karna hai|deal chahiye|offer chahiye|price kitna hai|discount milega|checkout karna hai|yeh pasand hai|yeh perfect hai|bahut accha hai|bahut badhiya hai|amazing lag raha hai|great deal|best price|recommend karunga|recommend karungi|approve karta hoon|approve karti hoon)'
        ]
        
        # Results storage
        self.results_dir = Path("sentiment_results")
        self.results_dir.mkdir(exist_ok=True)
        
    def _setup_device(self, device: str) -> str:
        """Setup the appropriate device for processing."""
        if device == "auto":
            if torch.cuda.is_available():
                return "cuda"
            elif torch.backends.mps.is_available():
                return "mps"
            else:
                return "cpu"
        return device
    
    def transcribe_audio(self, audio_path: str, language: Optional[str] = None) -> Dict:
        """
        Transcribe audio file using Whisper.
        
        Args:
            audio_path: Path to the audio file
            language: Language of the audio (optional)
            
        Returns:
            Dictionary containing transcription results
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        logger.info(f"Transcribing audio: {audio_path}")
        
        # Transcribe with word-level timestamps for better analysis
        result = self.whisper_model.transcribe(
            audio_path,
            language=language,
            word_timestamps=True,
            verbose=False
        )
        
        return result
    
    def analyze_sentiment(self, text: str) -> Tuple[float, float]:
        """
        Analyze sentiment of text using TextBlob.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (sentiment_score, confidence)
        """
        blob = TextBlob(text)
        sentiment = blob.sentiment
        
        # Convert polarity (-1 to 1) to sentiment score
        sentiment_score = sentiment.polarity
        confidence = abs(sentiment_score)  # Higher absolute value = higher confidence
        
        return sentiment_score, confidence
    
    def detect_purchase_intent(self, text: str, segments: List[Dict] = None) -> Tuple[bool, float, List[str]]:
        """
        Detect purchase intention from transcribed text.
        
        Args:
            text: Transcribed text
            segments: Optional segments with timestamps
            
        Returns:
            Tuple of (has_intent, confidence, key_phrases)
        """
        text_lower = text.lower()
        key_phrases = []
        intent_score = 0.0
        
        # Check for intent patterns
        for pattern in self.intent_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                key_phrases.extend(matches)
                intent_score += 0.2
        
        # Check for positive purchase keywords
        positive_count = sum(1 for word in self.purchase_positive_keywords 
                           if word in text_lower)
        
        # Check for negative purchase keywords
        negative_count = sum(1 for word in self.purchase_negative_keywords 
                           if word in text_lower)
        
        # Calculate intent score
        if positive_count > 0:
            intent_score += min(positive_count * 0.1, 0.5)
        
        if negative_count > 0:
            intent_score -= min(negative_count * 0.1, 0.3)
        
        # Add context from key phrases
        for phrase in key_phrases:
            if any(pos_word in phrase.lower() for pos_word in self.purchase_positive_keywords):
                intent_score += 0.15
        
        # Normalize score to 0-1 range
        confidence = max(0, min(1, intent_score))
        has_intent = confidence > 0.3  # Threshold for purchase intent
        
        return has_intent, confidence, key_phrases
    
    def extract_emotions(self, text: str) -> Dict[str, float]:
        """
        Extract emotional indicators from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary of emotion scores
        """
        emotions = {
            'excitement': 0.0,
            'satisfaction': 0.0,
            'frustration': 0.0,
            'uncertainty': 0.0,
            'enthusiasm': 0.0
        }

        text_lower = text.lower()

        # Excitement indicators (English + Hindi)
        excitement_words = [
            'amazing', 'fantastic', 'incredible', 'awesome', 'wow', 'perfect',
            'अद्भुत', 'शानदार', 'कमाल', 'वाह', 'सही', 'बढ़िया', 'adbhut', 'shandar', 'kamal', 'wah', 'sahi', 'badhiya'
        ]
        emotions['excitement'] = sum(1 for word in excitement_words if word in text_lower) * 0.2

        # Satisfaction indicators
        satisfaction_words = [
            'satisfied', 'happy', 'pleased', 'good', 'great', 'excellent',
            'संतुष्ट', 'खुश', 'प्रसन्न', 'अच्छा', 'उत्तम', 'शानदार', 'santusht', 'khush', 'prasann', 'accha', 'uttam', 'shandar'
        ]
        emotions['satisfaction'] = sum(1 for word in satisfaction_words if word in text_lower) * 0.15

        # Frustration indicators
        frustration_words = [
            'frustrated', 'angry', 'annoyed', 'terrible', 'awful', 'hate',
            'नाराज', 'गुस्सा', 'परेशान', 'खराब', 'बुरा', 'नापसंद', 'naraz', 'gussa', 'pareshan', 'kharab', 'bura', 'napasand'
        ]
        emotions['frustration'] = sum(1 for word in frustration_words if word in text_lower) * 0.2

        # Uncertainty indicators
        uncertainty_words = [
            'maybe', 'perhaps', 'not sure', 'uncertain', 'confused', 'hesitant',
            'शायद', 'संभवतः', 'निश्चित नहीं', 'अनिश्चित', 'उलझन', 'हिचकिचाहट', 'shayad', 'sambhavta', 'nishchit nahi', 'anishchit', 'uljhan', 'hichkichahat'
        ]
        emotions['uncertainty'] = sum(1 for word in uncertainty_words if word in text_lower) * 0.2

        # Enthusiasm indicators
        enthusiasm_words = [
            'excited', 'eager', "can't wait", 'looking forward', 'love', 'adore',
            'उत्साहित', 'आतुर', 'इंतजार', 'प्रेम', 'प्यार', 'ador', 'utsahit', 'aatur', 'intezar', 'prem', 'pyaar'
        ]
        emotions['enthusiasm'] = sum(1 for word in enthusiasm_words if word in text_lower) * 0.2

        # Normalize scores
        for emotion in emotions:
            emotions[emotion] = min(1.0, emotions[emotion])

        return emotions
    
    def analyze_audio(self, audio_path: str, language: Optional[str] = None) -> SentimentResult:
        """
        Complete analysis pipeline for audio file.
        
        Args:
            audio_path: Path to audio file
            language: Language of the audio (optional, defaults to Hindi)
            
        Returns:
            SentimentResult object with complete analysis
        """
        # Use Hindi as default language if not specified
        if language is None:
            language = self.default_language
        transcription_result = self.transcribe_audio(audio_path, language)
        text = transcription_result['text'].strip()
        
        if not text:
            logger.warning("No text extracted from audio")
            return SentimentResult(
                text="",
                sentiment_score=0.0,
                confidence=0.0,
                purchase_intent=False,
                purchase_confidence=0.0,
                key_phrases=[],
                emotions={},
                timestamp=datetime.now().isoformat()
            )
        
        # Analyze sentiment
        sentiment_score, sentiment_confidence = self.analyze_sentiment(text)
        
        # Detect purchase intent
        purchase_intent, purchase_confidence, key_phrases = self.detect_purchase_intent(
            text, transcription_result.get('segments', [])
        )
        
        # Extract emotions
        emotions = self.extract_emotions(text)
        
        # Create result
        result = SentimentResult(
            text=text,
            sentiment_score=sentiment_score,
            confidence=sentiment_confidence,
            purchase_intent=purchase_intent,
            purchase_confidence=purchase_confidence,
            key_phrases=key_phrases,
            emotions=emotions,
            timestamp=datetime.now().isoformat()
        )
        
        return result
    
    def save_result(self, result: SentimentResult, audio_filename: str):
        """Save analysis result to JSON file."""
        filename = f"analysis_{Path(audio_filename).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.results_dir / filename
        
        result_dict = {
            'text': result.text,
            'sentiment_score': result.sentiment_score,
            'confidence': result.confidence,
            'purchase_intent': result.purchase_intent,
            'purchase_confidence': result.purchase_confidence,
            'key_phrases': result.key_phrases,
            'emotions': result.emotions,
            'timestamp': result.timestamp,
            'audio_file': audio_filename
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to: {filepath}")
    
    def print_analysis(self, result: SentimentResult):
        """Print formatted analysis results."""
        print("\n" + "="*60)
        print("CUSTOMER SENTIMENT ANALYSIS RESULTS")
        print("="*60)
        
        print(f"\nTranscribed Text:")
        print(f"'{result.text}'")
        
        print(f"\nSentiment Analysis:")
        sentiment_label = "Positive" if result.sentiment_score > 0.1 else "Negative" if result.sentiment_score < -0.1 else "Neutral"
        print(f"  Sentiment: {sentiment_label} (Score: {result.sentiment_score:.3f})")
        print(f"  Confidence: {result.confidence:.3f}")
        
        print(f"\nPurchase Intent Analysis:")
        intent_label = "HIGH" if result.purchase_confidence > 0.7 else "MEDIUM" if result.purchase_confidence > 0.4 else "LOW"
        print(f"  Purchase Intent: {'YES' if result.purchase_intent else 'NO'}")
        print(f"  Intent Strength: {intent_label} ({result.purchase_confidence:.3f})")
        
        if result.key_phrases:
            print(f"  Key Phrases: {', '.join(result.key_phrases)}")
        
        print(f"\nEmotional Analysis:")
        for emotion, score in result.emotions.items():
            if score > 0.1:  # Only show significant emotions
                print(f"  {emotion.title()}: {score:.2f}")
        
        print(f"\nAnalysis completed at: {result.timestamp}")
        print("="*60)


def main():
    """Example usage of the Customer Sentiment Analyzer."""
    # Initialize analyzer
    analyzer = CustomerSentimentAnalyzer(model_size="base.en")
    
    # Example usage - you would replace this with actual audio file paths
    audio_files = [
        # "customer_call_1.wav",
        # "product_review_1.mp3",
        # "sales_interaction.flac"
    ]
    
    if not audio_files:
        print("No audio files specified. Please add audio file paths to analyze.")
        print("\nExample usage:")
        print("analyzer = CustomerSentimentAnalyzer()")
        print("result = analyzer.analyze_audio('your_audio_file.wav')")
        print("analyzer.print_analysis(result)")
        return
    
    # Process each audio file
    for audio_file in audio_files:
        if os.path.exists(audio_file):
            try:
                print(f"\nProcessing: {audio_file}")
                result = analyzer.analyze_audio(audio_file)
                analyzer.print_analysis(result)
                analyzer.save_result(result, audio_file)
            except Exception as e:
                logger.error(f"Error processing {audio_file}: {str(e)}")
        else:
            logger.warning(f"Audio file not found: {audio_file}")


if __name__ == "__main__":
    main()
