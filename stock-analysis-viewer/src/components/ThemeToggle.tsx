'use client';

import React, { useState, useEffect } from 'react';

interface ThemeToggleProps {
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  position?: 'fixed' | 'relative';
}

export default function ThemeToggle({
  className = '',
  size = 'md',
  position = 'fixed'
}: ThemeToggleProps) {
  const [isDark, setIsDark] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    // Check if we're in the browser
    if (typeof window === 'undefined') return;

    // Get initial theme preference
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const shouldBeDark = savedTheme === 'dark' || (!savedTheme && prefersDark);

    setIsDark(shouldBeDark);
    updateTheme(shouldBeDark);
    setMounted(true);
  }, []);

  const updateTheme = (dark: boolean) => {
    if (typeof window === 'undefined') return;

    const html = document.documentElement;

    if (dark) {
      html.classList.add('dark');
      html.classList.remove('light');
    } else {
      html.classList.add('light');
      html.classList.remove('dark');
    }

    localStorage.setItem('theme', dark ? 'dark' : 'light');
  };

  const handleToggle = () => {
    const newDarkState = !isDark;
    setIsDark(newDarkState);
    updateTheme(newDarkState);
  };

  // Don't render until mounted to avoid hydration mismatch
  if (!mounted) {
    return (
      <div className={`${position === 'fixed' ? 'fixed top-4 right-4 z-50' : ''} ${className}`}>
        <div className="p-3 rounded-lg bg-white dark:bg-gray-800 shadow-lg border border-gray-200 dark:border-gray-700 animate-pulse">
          <div className="h-5 w-5 bg-gray-300 dark:bg-gray-600 rounded"></div>
        </div>
      </div>
    );
  }

  const sizeClasses = {
    sm: 'p-2',
    md: 'p-3',
    lg: 'p-4'
  };

  const iconSizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-5 w-5',
    lg: 'h-6 w-6'
  };

  const positionClasses = position === 'fixed' ? 'fixed top-4 right-4 z-50' : '';

  // Clean SVG icons
  const MoonIcon = () => (
    <svg
      className={`${iconSizeClasses[size]} text-gray-700 dark:text-gray-300 transition-colors duration-300`}
      fill="currentColor"
      viewBox="0 0 20 20"
    >
      <path
        fillRule="evenodd"
        d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"
        clipRule="evenodd"
      />
    </svg>
  );

  const SunIcon = () => (
    <svg
      className={`${iconSizeClasses[size]} text-yellow-500 dark:text-yellow-400 transition-colors duration-300`}
      fill="currentColor"
      viewBox="0 0 20 20"
    >
      <path
        fillRule="evenodd"
        d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z"
        clipRule="evenodd"
      />
    </svg>
  );

  return (
    <div className={`${positionClasses} ${className}`}>
      <button
        onClick={handleToggle}
        className={`${sizeClasses[size]} rounded-lg bg-white dark:bg-gray-800 shadow-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800`}
        aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
        title={`Switch to ${isDark ? 'light' : 'dark'} mode`}
      >
        {isDark ? <SunIcon /> : <MoonIcon />}
      </button>
    </div>
  );
}
