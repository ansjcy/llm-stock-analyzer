import React, { useState } from 'react';
import { HelpCircle, X } from 'lucide-react';

interface HelpTooltipProps {
  content: string;
  title?: string;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  position?: 'top' | 'bottom' | 'left' | 'right';
}

export default function HelpTooltip({ 
  content, 
  title, 
  className = '', 
  size = 'sm',
  position = 'top'
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
    top: 'top-full left-1/2 transform -translate-x-1/2 border-l-transparent border-r-transparent border-b-transparent border-t-gray-800 dark:border-t-gray-200',
    bottom: 'bottom-full left-1/2 transform -translate-x-1/2 border-l-transparent border-r-transparent border-t-transparent border-b-gray-800 dark:border-b-gray-200',
    left: 'left-full top-1/2 transform -translate-y-1/2 border-t-transparent border-b-transparent border-r-transparent border-l-gray-800 dark:border-l-gray-200',
    right: 'right-full top-1/2 transform -translate-y-1/2 border-t-transparent border-b-transparent border-l-transparent border-r-gray-800 dark:border-r-gray-200'
  };

  const shouldShow = isVisible || isHovered;

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
          <div className="bg-gray-800 dark:bg-gray-200 text-white dark:text-gray-800 text-sm rounded-lg shadow-xl p-4 border border-gray-700 dark:border-gray-300">
            {/* Close button for mobile */}
            <div className="flex justify-between items-start mb-2 md:hidden">
              {title && (
                <h4 className="font-semibold text-white dark:text-gray-800">{title}</h4>
              )}
              <button
                onClick={() => setIsVisible(false)}
                className="text-gray-300 hover:text-white dark:text-gray-600 dark:hover:text-gray-800"
              >
                <X size={16} />
              </button>
            </div>
            
            {/* Desktop title */}
            {title && (
              <h4 className="font-semibold text-white dark:text-gray-800 mb-2 hidden md:block">{title}</h4>
            )}
            
            <div className="text-gray-200 dark:text-gray-700 leading-relaxed whitespace-pre-line">
              {content}
            </div>
          </div>
          
          {/* Arrow */}
          <div className={`absolute w-0 h-0 border-4 ${arrowClasses[position]}`}></div>
        </div>
      )}
    </div>
  );
} 