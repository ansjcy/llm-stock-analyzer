'use client';

import React, { useState } from 'react';

export default function TestTheme() {
  const [isDark, setIsDark] = useState(false);

  const toggleTheme = () => {
    const newTheme = !isDark;
    setIsDark(newTheme);
    
    // Apply to document
    if (newTheme) {
      document.documentElement.classList.add('dark');
      document.body.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
      document.body.classList.remove('dark');
    }
    
    console.log('Theme toggled to:', newTheme ? 'dark' : 'light');
    console.log('HTML classes:', document.documentElement.className);
  };

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-black dark:text-white mb-8">
          Theme Test Page
        </h1>
        
        <button
          onClick={toggleTheme}
          className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 mb-8"
        >
          Toggle to {isDark ? 'Light' : 'Dark'} Mode
        </button>
        
        <div className="space-y-4">
          <div className="p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
              Test Card
            </h2>
            <p className="text-gray-600 dark:text-gray-300">
              This text should change color based on the theme.
            </p>
          </div>
          
          <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
            <h3 className="text-lg font-medium text-gray-800 dark:text-gray-200 mb-2">
              Border Test
            </h3>
            <p className="text-gray-500 dark:text-gray-400">
              The border and text colors should adapt to the theme.
            </p>
          </div>
        </div>
        
        <div className="mt-8 p-4 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
          <h3 className="text-lg font-semibold text-yellow-800 dark:text-yellow-200">
            Current State
          </h3>
          <p className="text-yellow-700 dark:text-yellow-300">
            Theme: {isDark ? 'Dark' : 'Light'}
          </p>
          <p className="text-yellow-600 dark:text-yellow-400 text-sm">
            HTML classes: {typeof window !== 'undefined' ? document.documentElement.className : 'Loading...'}
          </p>
        </div>
      </div>
    </div>
  );
}
