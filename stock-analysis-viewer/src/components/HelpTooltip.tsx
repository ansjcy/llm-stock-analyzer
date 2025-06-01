import React, { useState } from 'react';
import { HelpCircle, X } from 'lucide-react';

interface HelpTooltipProps {
  content: string;
  title?: string;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  position?: 'top' | 'bottom' | 'left' | 'right';
  colorMap?: Record<string, string>;
}

// Define default color mappings for technical indicators
const DEFAULT_COLOR_MAP: Record<string, string> = {
  '收盘价': '#3B82F6',
  'close': '#3B82F6',
  'SMA 20': '#10B981',
  'SMA 50': '#F59E0B',
  'SMA 200': '#DC2626',
  '布林带上轨': '#9CA3AF',
  '布林带下轨': '#9CA3AF',
  '布林带中轨': '#9CA3AF',
  '布林带区间': '#E5E7EB',
  '支撑位': '#16A34A',
  '阻力位': '#DC2626',
  'RSI': '#8B5CF6',
  'MACD': '#3B82F6',
  'MACD线': '#3B82F6',
  'MACD 线': '#3B82F6',
  '信号线': '#DC2626',
  'MACD 柱状图': '#9CA3AF',
  '成交量': '#6B7280',
  '成交量指标': '#6B7280',
  '绿色柱状图': '#10B981',
  '红色柱状图': '#EF4444'
};

// Function to parse and format content with markdown-like syntax and colors
const parseContent = (content: string, colorMap: Record<string, string>): React.ReactNode[] => {
  const lines = content.split('\n');
  const elements: React.ReactNode[] = [];
  
  lines.forEach((line, lineIndex) => {
    if (line.trim() === '') {
      elements.push(<br key={`br-${lineIndex}`} />);
      return;
    }
    
    let partIndex = 0;
    
    // Check for bullet points
    const isBulletPoint = line.trim().startsWith('- ');
    const cleanLine = isBulletPoint ? line.trim().substring(2) : line;
    
    // Check for headers (lines containing **)
    const isHeader = cleanLine.includes('**') && cleanLine.endsWith('**：');
    
    // Parse the line content
    const parseLineContent = (text: string): React.ReactNode[] => {
      const parts: React.ReactNode[] = [];
      
      // Handle bold text (**text**)
      const boldRegex = /\*\*(.*?)\*\*/g;
      let lastIndex = 0;
      let match;
      
      while ((match = boldRegex.exec(text)) !== null) {
        // Add text before the bold part
        if (match.index > lastIndex) {
          const beforeText = text.slice(lastIndex, match.index);
          parts.push(...colorizeText(beforeText, colorMap, partIndex));
        }
        
        // Add the bold part (and try to colorize it too)
        const boldContent = colorizeText(match[1], colorMap, partIndex);
        parts.push(
          <strong key={`bold-${partIndex++}`} className="font-semibold">
            {boldContent}
          </strong>
        );
        
        lastIndex = match.index + match[0].length;
      }
      
      // Add remaining text
      if (lastIndex < text.length) {
        const remainingText = text.slice(lastIndex);
        parts.push(...colorizeText(remainingText, colorMap, partIndex));
      }
      
      return parts.length > 0 ? parts : [text];
    };
    
    // Function to colorize text based on indicators
    const colorizeText = (text: string, colorMap: Record<string, string>, baseIndex: number): React.ReactNode[] => {
      let currentParts: React.ReactNode[] = [text];
      let usedIndex = baseIndex;
      
      // Sort indicators by length (longest first) to avoid partial matches
      const sortedIndicators = Object.keys(colorMap).sort((a, b) => b.length - a.length);
      
      // Process each indicator sequentially
      for (const indicator of sortedIndicators) {
        const newParts: React.ReactNode[] = [];
        
        for (const part of currentParts) {
          if (typeof part === 'string' && part.includes(indicator)) {
            const regex = new RegExp(`(${indicator.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
            const splits = part.split(regex);
            
            splits.forEach(split => {
              if (split.toLowerCase() === indicator.toLowerCase()) {
                newParts.push(
                  <span 
                    key={`colored-${usedIndex++}`}
                    style={{ 
                      color: colorMap[indicator],
                      fontWeight: '600',
                      backgroundColor: `${colorMap[indicator]}20`,
                      padding: '1px 4px',
                      borderRadius: '3px',
                      fontSize: '0.9em'
                    }}
                  >
                    {split}
                  </span>
                );
              } else if (split) {
                newParts.push(split);
              }
            });
          } else {
            // Keep non-string parts (already colored) as-is
            newParts.push(part);
          }
        }
        
        currentParts = newParts;
      }
      
      return currentParts.length > 0 ? currentParts : [text];
    };
    
    const lineContent = parseLineContent(cleanLine);
    
    if (isHeader) {
      elements.push(
        <div key={`header-${lineIndex}`} className="font-bold text-blue-200 mb-2 text-base border-b border-gray-500 pb-1">
          {lineContent}
        </div>
      );
    } else if (isBulletPoint) {
      elements.push(
        <div key={`bullet-${lineIndex}`} className="flex items-start mb-2 ml-2">
          <span className="text-blue-300 mr-2 mt-1 text-xs flex-shrink-0">•</span>
          <span className="text-sm leading-relaxed flex-1 text-gray-200">{lineContent}</span>
        </div>
      );
    } else {
      elements.push(
        <div key={`line-${lineIndex}`} className="mb-2 text-sm leading-relaxed text-gray-200">
          {lineContent}
        </div>
      );
    }
  });
  
  return elements;
};

export default function HelpTooltip({ 
  content, 
  title, 
  className = '', 
  size = 'sm',
  position = 'top',
  colorMap = {}
}: HelpTooltipProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6'
  };

  const positionClasses = {
    top: 'bottom-full left-1/2 transform -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 transform -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 transform -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 transform -translate-y-1/2 ml-2'
  };

  const arrowClasses = {
    top: 'top-full left-1/2 transform -translate-x-1/2 border-l-transparent border-r-transparent border-b-transparent border-t-gray-900',
    bottom: 'bottom-full left-1/2 transform -translate-x-1/2 border-l-transparent border-r-transparent border-t-transparent border-b-gray-900',
    left: 'left-full top-1/2 transform -translate-y-1/2 border-t-transparent border-b-transparent border-r-transparent border-l-gray-900',
    right: 'right-full top-1/2 transform -translate-y-1/2 border-t-transparent border-b-transparent border-l-transparent border-r-gray-900'
  };

  const shouldShow = isVisible || isHovered;
  const mergedColorMap = { ...DEFAULT_COLOR_MAP, ...colorMap };
  const formattedContent = parseContent(content, mergedColorMap);

  return (
    <div className={`relative inline-block ${className}`}>
      <button
        onClick={() => setIsVisible(!isVisible)}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        className="inline-flex items-center justify-center text-gray-400 hover:text-blue-600 dark:text-gray-500 dark:hover:text-blue-400 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 rounded-full"
        aria-label="帮助信息"
      >
        <HelpCircle className={sizeClasses[size]} />
      </button>

      {shouldShow && (
        <div className={`absolute z-50 ${positionClasses[position]} w-80 max-w-sm`}>
          <div className="bg-gray-900 text-gray-200 rounded-lg shadow-xl p-4 border border-gray-600">
            {/* Close button for mobile */}
            <div className="flex justify-between items-start mb-2 md:hidden">
              {title && (
                <h4 className="font-semibold text-blue-200">{title}</h4>
              )}
              <button
                onClick={() => setIsVisible(false)}
                className="text-gray-400 hover:text-gray-200"
              >
                <X size={16} />
              </button>
            </div>
            
            {/* Desktop title */}
            {title && (
              <h4 className="font-semibold text-blue-200 mb-3 hidden md:block border-b border-gray-600 pb-2">
                {title}
              </h4>
            )}
            
            <div className="space-y-1">
              {formattedContent}
            </div>
          </div>
          
          {/* Arrow */}
          <div className={`absolute w-0 h-0 border-4 ${arrowClasses[position]}`}></div>
        </div>
      )}
    </div>
  );
} 