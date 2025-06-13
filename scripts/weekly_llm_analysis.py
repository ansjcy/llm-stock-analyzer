#!/usr/bin/env python3
"""
Weekly LLM Analysis Script

This script automates the weekly LLM analysis process by:
1. Finding the latest base analysis files for specified tickers
2. Running LLM-only analysis on each ticker
3. Creating merged complete reports

Usage:
    python scripts/weekly_llm_analysis.py --tickers AAPL,MSFT,GOOGL
    python scripts/weekly_llm_analysis.py --all-recent  # Process all tickers with base files from last 7 days
"""

import os
import sys
import glob
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def find_latest_base_file(ticker: str, reports_dir: str = "stock-analysis-viewer/public/reports") -> str:
    """Find the latest base analysis file for a given ticker"""
    pattern = f"{reports_dir}/{ticker}_analysis_base_*.json"
    base_files = glob.glob(pattern)
    
    if not base_files:
        return None
    
    # Sort by modification time, newest first
    base_files.sort(key=os.path.getmtime, reverse=True)
    return base_files[0]

def find_recent_tickers(reports_dir: str = "stock-analysis-viewer/public/reports", days: int = 7) -> list:
    """Find all tickers with base files created in the last N days"""
    cutoff_date = datetime.now() - timedelta(days=days)
    pattern = f"{reports_dir}/*_analysis_base_*.json"
    base_files = glob.glob(pattern)
    
    recent_tickers = set()
    for file_path in base_files:
        # Check if file was modified recently
        if datetime.fromtimestamp(os.path.getmtime(file_path)) > cutoff_date:
            # Extract ticker from filename
            filename = os.path.basename(file_path)
            ticker = filename.split('_analysis_base_')[0]
            recent_tickers.add(ticker)
    
    return sorted(list(recent_tickers))

def run_llm_analysis(ticker: str, base_file_path: str, format_type: str = "json") -> bool:
    """Run LLM-only analysis for a ticker using its base file"""
    print(f"\n🔄 Processing {ticker}...")
    print(f"   Base file: {os.path.basename(base_file_path)}")
    
    cmd = [
        "python", "src/main.py",
        "--llm-only",
        "--base-data-path", base_file_path,
        "--save-report",
        "--format", format_type
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print(f"✅ {ticker} analysis completed successfully")
            return True
        else:
            print(f"❌ {ticker} analysis failed:")
            print(f"   Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {ticker} analysis timed out (10 minutes)")
        return False
    except Exception as e:
        print(f"❌ {ticker} analysis failed with exception: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Weekly LLM Analysis Automation")
    parser.add_argument("--tickers", help="Comma-separated list of tickers to process")
    parser.add_argument("--all-recent", action="store_true", 
                       help="Process all tickers with base files from last 7 days")
    parser.add_argument("--days", type=int, default=7,
                       help="Number of days to look back for recent files (default: 7)")
    parser.add_argument("--format", choices=["json", "markdown"], default="json",
                       help="Output format (default: json)")
    parser.add_argument("--reports-dir", default="stock-analysis-viewer/public/reports",
                       help="Reports directory path")
    
    args = parser.parse_args()
    
    if not args.tickers and not args.all_recent:
        print("❌ Error: Must specify either --tickers or --all-recent")
        sys.exit(1)
    
    # Change to project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)
    
    print("🚀 Weekly LLM Analysis Script")
    print("=" * 50)
    
    # Determine which tickers to process
    if args.all_recent:
        tickers = find_recent_tickers(args.reports_dir, args.days)
        print(f"📊 Found {len(tickers)} tickers with recent base files (last {args.days} days):")
        for ticker in tickers:
            print(f"   • {ticker}")
    else:
        tickers = [t.strip().upper() for t in args.tickers.split(',') if t.strip()]
        print(f"📊 Processing specified tickers: {', '.join(tickers)}")
    
    if not tickers:
        print("❌ No tickers to process")
        sys.exit(1)
    
    # Process each ticker
    successful = 0
    failed = 0
    
    for ticker in tickers:
        base_file = find_latest_base_file(ticker, args.reports_dir)
        
        if not base_file:
            print(f"\n⚠️  {ticker}: No base analysis file found")
            failed += 1
            continue
        
        if run_llm_analysis(ticker, base_file, args.format):
            successful += 1
        else:
            failed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("📈 Weekly LLM Analysis Summary")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {len(tickers)}")
    
    if successful > 0:
        print(f"\n🎉 {successful} complete merged reports have been generated!")
        print("   These files contain both base analysis + LLM insights")

if __name__ == "__main__":
    main()
