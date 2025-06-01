#!/usr/bin/env python3
"""
Demo script to show the new detailed logging functionality.
This script demonstrates the enhanced LLM analysis logging.
"""

import os
import sys
import subprocess

def main():
    print("🔍 Demonstrating Enhanced LLM Analysis Logging")
    print("=" * 60)
    
    # Test ticker
    ticker = "AAPL"
    
    print(f"This demo will show the new detailed logging for LLM analysis.")
    print(f"You'll see exactly what step is being executed and progress indicators.")
    print(f"")
    print(f"Testing with ticker: {ticker}")
    print(f"")
    
    # Step 1: Generate base analysis
    print("Step 1: Generating base analysis (no LLM)")
    print("-" * 40)
    
    cmd1 = f"python src/main.py --ticker {ticker} --save-report --format json --non-llm-only --chinese"
    print(f"Command: {cmd1}")
    print("")
    
    try:
        result1 = subprocess.run(cmd1, shell=True, text=True, timeout=120)
        if result1.returncode == 0:
            print("✅ Base analysis completed successfully!")
        else:
            print("❌ Base analysis failed!")
            return 1
    except subprocess.TimeoutExpired:
        print("⏰ Base analysis timed out!")
        return 1
    except Exception as e:
        print(f"💥 Error in base analysis: {e}")
        return 1
    
    # Step 2: Find the base file
    reports_dir = "./stock-analysis-viewer/public/reports"
    base_files = [f for f in os.listdir(reports_dir) if f.startswith(f"{ticker}_analysis_base_")]
    
    if not base_files:
        print("❌ No base file found! Cannot proceed with LLM demo.")
        return 1
    
    base_file_path = os.path.join(reports_dir, base_files[0])
    print(f"✅ Found base file: {base_file_path}")
    print("")
    
    # Step 2: Generate LLM analysis with detailed logging
    print("Step 2: Generating LLM analysis with detailed logging")
    print("-" * 50)
    print("Watch for the following detailed progress indicators:")
    print("  → Processing steps with descriptions")
    print("  → LLM API call notifications (30-60 seconds each)")
    print("  → Success/failure status with character counts")
    print("  → Error handling if any step fails")
    print("")
    
    cmd2 = f"python src/main.py --ticker {ticker} --save-report --format json --llm-only --base-data-path {base_file_path} --chinese"
    print(f"Command: {cmd2}")
    print("")
    print("🚀 Starting LLM analysis with enhanced logging...")
    print("=" * 60)
    
    try:
        # Run with real-time output
        process = subprocess.Popen(
            cmd2, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Print output in real-time
        for line in process.stdout:
            print(line.rstrip())
        
        process.wait()
        
        if process.returncode == 0:
            print("")
            print("=" * 60)
            print("✅ LLM analysis completed successfully!")
            print("")
            print("🎯 Key improvements you should have seen:")
            print("  ✓ Clear step-by-step progress descriptions")
            print("  ✓ Notifications before each LLM API call")
            print("  ✓ Success confirmations with response lengths")
            print("  ✓ Error handling with specific error messages")
            print("  ✓ Overall progress tracking")
            print("")
            
            # Check if LLM file was created
            llm_files = [f for f in os.listdir(reports_dir) if f.startswith(f"{ticker}_analysis_llm_")]
            if llm_files:
                print(f"✅ LLM file created: {llm_files[0]}")
            else:
                print("⚠️  LLM file not found (check for errors above)")
            
            return 0
        else:
            print("")
            print("=" * 60)
            print("❌ LLM analysis failed!")
            print("But you should have seen detailed error messages above.")
            return 1
            
    except subprocess.TimeoutExpired:
        print("⏰ LLM analysis timed out!")
        return 1
    except Exception as e:
        print(f"💥 Error in LLM analysis: {e}")
        return 1

if __name__ == "__main__":
    print("Note: Make sure you have GEMINI_API_KEY set in your environment")
    print("      or the LLM analysis will fail (but you'll see detailed error messages)")
    print("")
    
    # Check if API key is available
    if not os.getenv('GEMINI_API_KEY') and not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Warning: No LLM API keys found in environment")
        print("   Set GEMINI_API_KEY or OPENAI_API_KEY to see full LLM analysis")
        print("   You can still see the detailed logging for error handling")
        print("")
    
    sys.exit(main())
