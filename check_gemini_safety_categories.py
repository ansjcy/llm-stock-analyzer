#!/usr/bin/env python3
"""
Check valid Gemini safety categories
"""

import google.generativeai as genai

def check_safety_categories():
    """Check what safety categories are available in the Gemini API"""
    
    print("🔍 Checking available Gemini safety categories...")
    
    # Try to access the safety settings enum
    try:
        # Check if there's a HarmCategory enum
        if hasattr(genai.types, 'HarmCategory'):
            harm_category = genai.types.HarmCategory
            print("✅ Found HarmCategory enum:")
            for attr in dir(harm_category):
                if not attr.startswith('_'):
                    print(f"   - {attr}")
        else:
            print("❌ HarmCategory enum not found in genai.types")
            
        # Check if there's a HarmBlockThreshold enum
        if hasattr(genai.types, 'HarmBlockThreshold'):
            harm_threshold = genai.types.HarmBlockThreshold
            print("\n✅ Found HarmBlockThreshold enum:")
            for attr in dir(harm_threshold):
                if not attr.startswith('_'):
                    print(f"   - {attr}")
        else:
            print("❌ HarmBlockThreshold enum not found in genai.types")
            
    except Exception as e:
        print(f"❌ Error checking safety categories: {e}")
        
    # Print the standard categories we know work
    print("\n📋 Standard safety categories that should work:")
    standard_categories = [
        "HARM_CATEGORY_HARASSMENT",
        "HARM_CATEGORY_HATE_SPEECH", 
        "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "HARM_CATEGORY_DANGEROUS_CONTENT"
    ]
    
    for category in standard_categories:
        print(f"   - {category}")
        
    print("\n📋 Standard thresholds:")
    thresholds = [
        "BLOCK_NONE",
        "BLOCK_ONLY_HIGH", 
        "BLOCK_MEDIUM_AND_ABOVE",
        "BLOCK_LOW_AND_ABOVE"
    ]
    
    for threshold in thresholds:
        print(f"   - {threshold}")

if __name__ == "__main__":
    check_safety_categories()
