#!/bin/bash

# Stock Analysis and Web Viewer Script
# Usage: ./scripts/analyze-and-view.sh TICKER [LANGUAGE]
# Example: ./scripts/analyze-and-view.sh AAPL
# Example: ./scripts/analyze-and-view.sh AAPL chinese

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if ticker is provided
if [ $# -eq 0 ]; then
    print_error "Please provide a stock ticker symbol"
    echo "Usage: $0 TICKER [LANGUAGE]"
    echo "Example: $0 AAPL"
    echo "Example: $0 AAPL chinese"
    exit 1
fi

TICKER=$1
LANGUAGE=${2:-"english"}

# Check if we're in the correct directory
if [ ! -f "package.json" ] || [ ! -d "src" ]; then
    print_error "Please run this script from the stock-analysis-viewer directory"
    exit 1
fi

# Check if the LLM stock analysis tool exists
LLM_TOOL_DIR="../llm-stock-analysis"
if [ ! -d "$LLM_TOOL_DIR" ]; then
    print_error "LLM Stock Analysis Tool not found at $LLM_TOOL_DIR"
    print_warning "Please ensure the llm-stock-analysis directory is at the same level as stock-analysis-viewer"
    exit 1
fi

print_status "Starting stock analysis for $TICKER..."

# Create reports directory if it doesn't exist
mkdir -p reports

# Generate timestamp for unique filename
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="reports/${TICKER}_analysis_${TIMESTAMP}.json"

# Build the analysis command
ANALYSIS_CMD="python src/main.py --ticker $TICKER --detailed --save-report --format json --output $OUTPUT_FILE"

# Add language flag if specified
if [ "$LANGUAGE" = "chinese" ]; then
    ANALYSIS_CMD="$ANALYSIS_CMD --chinese"
    print_status "Generating analysis in Chinese..."
else
    print_status "Generating analysis in English..."
fi

# Run the analysis
print_status "Running: $ANALYSIS_CMD"
cd "$LLM_TOOL_DIR"

if eval "$ANALYSIS_CMD"; then
    print_success "Analysis completed successfully!"
    
    # Go back to the web viewer directory
    cd - > /dev/null
    
    # Check if the output file was created
    FULL_OUTPUT_PATH="$LLM_TOOL_DIR/$OUTPUT_FILE"
    if [ -f "$FULL_OUTPUT_PATH" ]; then
        # Copy the file to the web viewer's public directory for easy access
        cp "$FULL_OUTPUT_PATH" "public/latest-analysis.json"
        print_success "Analysis file saved to public/latest-analysis.json"
        
        # Check if the web server is running
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            print_success "Web viewer is already running at http://localhost:3000"
            print_status "You can now upload the analysis file: $FULL_OUTPUT_PATH"
            
            # Try to open the browser (works on macOS and most Linux distributions)
            if command -v open > /dev/null 2>&1; then
                open http://localhost:3000
            elif command -v xdg-open > /dev/null 2>&1; then
                xdg-open http://localhost:3000
            else
                print_warning "Could not automatically open browser. Please navigate to http://localhost:3000"
            fi
        else
            print_warning "Web viewer is not running. Starting it now..."
            print_status "Starting Next.js development server..."
            
            # Start the development server in the background
            npm run dev &
            DEV_SERVER_PID=$!
            
            # Wait a moment for the server to start
            sleep 5
            
            # Check if it's running now
            if curl -s http://localhost:3000 > /dev/null 2>&1; then
                print_success "Web viewer started successfully at http://localhost:3000"
                
                # Try to open the browser
                if command -v open > /dev/null 2>&1; then
                    open http://localhost:3000
                elif command -v xdg-open > /dev/null 2>&1; then
                    xdg-open http://localhost:3000
                else
                    print_warning "Could not automatically open browser. Please navigate to http://localhost:3000"
                fi
            else
                print_error "Failed to start web viewer"
                exit 1
            fi
        fi
        
        echo ""
        print_success "🎉 Analysis complete! Next steps:"
        echo "1. Open http://localhost:3000 in your browser"
        echo "2. Upload the analysis file: $FULL_OUTPUT_PATH"
        echo "3. Or click 'View Sample Data' to load the latest analysis automatically"
        
    else
        print_error "Analysis file was not created at expected location: $FULL_OUTPUT_PATH"
        exit 1
    fi
else
    print_error "Analysis failed. Please check the error messages above."
    exit 1
fi 