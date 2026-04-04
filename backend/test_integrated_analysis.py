#!/usr/bin/env python3
"""Test script for integrated emotion detection in analyze-text endpoint"""
import json
from app.services.text_analyzer import TextAnalyzerService
from app.services.emotion_detector import EmotionDetectorService


def test_integrated_analysis():
    """Test integrated text analysis with emotion detection"""
    test_cases = [
        {
            "text": "jajaja esto es hilariante!!!",
            "expected_emotion": "risa",
            "expected_sentiment": "positive"
        },
        {
            "text": "no puede ser increíble wow!",
            "expected_emotion": "sorpresa",
            "expected_sentiment": "positive"
        },
        {
            "text": "¡¡¡estoy muy enojado!!!",
            "expected_emotion": "enojo",
            "expected_sentiment": "negative"
        },
        {
            "text": "me siento tan triste... adiós",
            "expected_emotion": "tristeza",
            "expected_sentiment": "negative"
        },
        {
            "text": "claro que sí, seguro",
            "expected_emotion": "sarcasmo",
            "expected_sentiment": "neutral"
        },
        {
            "text": "no entiendo ¿qué pasa?",
            "expected_emotion": "confusión",
            "expected_sentiment": "neutral"
        }
    ]
    
    print("\n" + "=" * 80)
    print("INTEGRATED ANALYSIS TEST - TEXT ANALYSIS WITH EMOTION DETECTION")
    print("=" * 80 + "\n")
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        text = test_case["text"]
        expected_emotion = test_case["expected_emotion"]
        
        # Get text analysis
        analyzer = TextAnalyzerService()
        analysis = analyzer.analyze(text)
        
        # Get emotion detection
        emotion_detector = EmotionDetectorService()
        emotion = emotion_detector.detect(text)
        
        # Combine results (simulating the endpoint)
        combined = {
            **analysis,
            "emotion": emotion.get("emotion"),
            "emotion_intensity": emotion.get("intensity"),
            "emotion_intensity_level": emotion.get("intensity_level"),
            "emotion_confidence": emotion.get("confidence"),
        }
        
        # Display results
        print(f"Test {i}:")
        print(f"  📝 Text: {text!r}")
        print(f"  🎭 Emotion: {combined['emotion']} (confidence: {combined['emotion_confidence']})")
        print(f"  💪 Intensity: {combined['emotion_intensity']}/1.0 ({combined['emotion_intensity_level']})")
        print(f"  😊 Sentiment: {combined['sentiment']}")
        print(f"  📌 Theme: {combined['theme']}")
        print(f"  🔑 Keywords: {', '.join(combined['keywords'])}")
        
        # Check if emotion matches expected
        if combined['emotion'] == expected_emotion:
            print(f"  ✅ PASS - Emotion matched")
            passed += 1
        else:
            print(f"  ❌ FAIL - Expected {expected_emotion}, got {combined['emotion']}")
            failed += 1
        
        print()
    
    print("=" * 80)
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 80 + "\n")
    
    return failed == 0


def test_response_format():
    """Test that response format is correct"""
    print("\n" + "=" * 80)
    print("RESPONSE FORMAT TEST")
    print("=" * 80 + "\n")
    
    text = "jajaja no puede ser!"
    
    # Get text analysis
    analyzer = TextAnalyzerService()
    analysis = analyzer.analyze(text)
    
    # Get emotion detection
    emotion_detector = EmotionDetectorService()
    emotion = emotion_detector.detect(text)
    
    # Combine results
    response = {
        **analysis,
        "emotion": emotion.get("emotion"),
        "emotion_intensity": emotion.get("intensity"),
        "emotion_intensity_level": emotion.get("intensity_level"),
        "emotion_confidence": emotion.get("confidence"),
    }
    
    print("Response JSON:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    # Verify all required fields
    required_fields = [
        "text", "keywords", "sentiment", "theme",
        "emotion", "emotion_intensity", "emotion_intensity_level", "emotion_confidence"
    ]
    
    print("\nField validation:")
    all_present = True
    for field in required_fields:
        if field in response:
            print(f"  ✅ {field}: {type(response[field]).__name__}")
        else:
            print(f"  ❌ {field}: MISSING")
            all_present = False
    
    print()
    return all_present


if __name__ == "__main__":
    format_ok = test_response_format()
    tests_pass = test_integrated_analysis()
    
    if format_ok and tests_pass:
        print("✨ ALL TESTS PASSED! The integration is working correctly.\n")
    else:
        print("⚠️  Some tests failed. Check the output above.\n")
