#!/usr/bin/env python3
"""
Command Line Interface for Customer Sentiment Analysis

Simple CLI tool to analyze audio files for customer sentiment and purchase intentions.
"""

import argparse
import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from customer_sentiment_analyzer import CustomerSentimentAnalyzer, SentimentResult
except ImportError as e:
    print(f"Error: Could not import sentiment analyzer. {str(e)}")
    print("Please install required dependencies first:")
    print("pip install -r requirements_extended.txt")
    sys.exit(1)


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Analyze audio files for customer sentiment and purchase intentions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s customer_call.wav
  %(prog)s --model small.en --language en audio1.mp3 audio2.wav
  %(prog)s --batch audio_files/
  %(prog)s --output results.json customer_review.flac
        """
    )
    
    parser.add_argument(
        'audio_files',
        nargs='+',
        help='Audio file(s) or directory to analyze'
    )
    
    parser.add_argument(
        '--model',
        default='base.en',
        choices=['tiny.en', 'base.en', 'small.en', 'medium.en', 'tiny', 'base', 'small', 'medium', 'large'],
        help='Whisper model to use (default: base.en)'
    )
    
    parser.add_argument(
        '--language',
        default=None,
        help='Language of the audio (e.g., "en", "es", "fr"). Auto-detect if not specified.'
    )
    
    parser.add_argument(
        '--output',
        help='Output file to save results (JSON format)'
    )
    
    parser.add_argument(
        '--batch',
        action='store_true',
        help='Process directory recursively for audio files'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress detailed output, show only summary'
    )
    
    parser.add_argument(
        '--save-results',
        action='store_true',
        default=True,
        help='Save results to individual JSON files (default: True)'
    )
    
    args = parser.parse_args()
    
    # Initialize analyzer
    if not args.quiet:
        print(f"Initializing Whisper model: {args.model}")
    
    try:
        analyzer = CustomerSentimentAnalyzer(model_size=args.model)
    except Exception as e:
        print(f"Error: Failed to initialize analyzer: {str(e)}")
        sys.exit(1)
    
    # Collect audio files
    audio_files = []
    audio_extensions = {'.wav', '.mp3', '.flac', '.m4a', '.ogg', '.aac'}
    
    for path_str in args.audio_files:
        path = Path(path_str)
        
        if path.is_file():
            if path.suffix.lower() in audio_extensions:
                audio_files.append(path)
            else:
                print(f"Warning: Skipping non-audio file: {path}")
        
        elif path.is_dir() and args.batch:
            for ext in audio_extensions:
                audio_files.extend(path.rglob(f"*{ext}"))
        
        elif path.is_dir():
            print(f"Warning: {path} is a directory. Use --batch to process directories.")
        
        else:
            print(f"Warning: File not found: {path}")
    
    if not audio_files:
        print("Error: No valid audio files found.")
        sys.exit(1)
    
    # Process files
    results = []
    
    for i, audio_file in enumerate(audio_files, 1):
        if not args.quiet:
            print(f"\n[{i}/{len(audio_files)}] Processing: {audio_file.name}")
        
        try:
            result = analyzer.analyze_audio(str(audio_file), language=args.language)
            
            if not args.quiet:
                analyzer.print_analysis(result)
            else:
                # Quiet mode summary
                intent_status = "YES" if result.purchase_intent else "NO"
                sentiment_label = "Positive" if result.sentiment_score > 0.1 else "Negative" if result.sentiment_score < -0.1 else "Neutral"
                print(f"{audio_file.name}: {sentiment_label} sentiment, Purchase intent: {intent_status}")
            
            # Save individual result file
            if args.save_results:
                analyzer.save_result(result, str(audio_file))
            
            # Add to results for batch output
            results.append({
                'file': str(audio_file),
                'text': result.text,
                'sentiment_score': result.sentiment_score,
                'confidence': result.confidence,
                'purchase_intent': result.purchase_intent,
                'purchase_confidence': result.purchase_confidence,
                'key_phrases': result.key_phrases,
                'emotions': result.emotions,
                'timestamp': result.timestamp
            })
            
        except Exception as e:
            print(f"Error processing {audio_file}: {str(e)}")
            continue
    
    # Save batch results if requested
    if args.output:
        import json
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\nBatch results saved to: {args.output}")
        except Exception as e:
            print(f"Error saving results: {str(e)}")
    
    # Final summary
    if not args.quiet and len(results) > 1:
        print("\n" + "="*60)
        print("BATCH ANALYSIS SUMMARY")
        print("="*60)
        
        total_files = len(results)
        positive_sentiment = sum(1 for r in results if r['sentiment_score'] > 0.1)
        negative_sentiment = sum(1 for r in results if r['sentiment_score'] < -0.1)
        purchase_intent = sum(1 for r in results if r['purchase_intent'])
        
        print(f"Files processed: {total_files}")
        print(f"Positive sentiment: {positive_sentiment} ({positive_sentiment/total_files*100:.1f}%)")
        print(f"Negative sentiment: {negative_sentiment} ({negative_sentiment/total_files*100:.1f}%)")
        print(f"Purchase intent detected: {purchase_intent} ({purchase_intent/total_files*100:.1f}%)")
        
        if purchase_intent > 0:
            avg_confidence = sum(r['purchase_confidence'] for r in results if r['purchase_intent']) / purchase_intent
            print(f"Average purchase intent confidence: {avg_confidence:.3f}")
        
        print("="*60)


if __name__ == '__main__':
    main()
