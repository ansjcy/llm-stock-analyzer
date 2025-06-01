'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';

type Theme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
  mounted: boolean;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// Function to get initial theme
function getInitialTheme(): Theme {
  if (typeof window === 'undefined') return 'light';

  try {
    const savedTheme = localStorage.getItem('theme') as Theme;
    if (savedTheme && (savedTheme === 'light' || savedTheme === 'dark')) {
      return savedTheme;
    }

    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
  } catch (error) {
    console.warn('Error accessing localStorage or matchMedia:', error);
  }

  return 'light';
}

// Function to apply theme to document
function applyTheme(theme: Theme) {
  if (typeof window === 'undefined') return;

  const root = window.document.documentElement;
  const body = window.document.body;

  // Remove existing theme classes
  root.classList.remove('light', 'dark');
  body.classList.remove('light', 'dark');

  // Add new theme class
  root.classList.add(theme);
  body.classList.add(theme);

  try {
    localStorage.setItem('theme', theme);
  } catch (error) {
    console.warn('Error saving theme to localStorage:', error);
  }
}

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>('light');
  const [mounted, setMounted] = useState(false);

  // Initialize theme on mount
  useEffect(() => {
    const initialTheme = getInitialTheme();
    setTheme(initialTheme);
    applyTheme(initialTheme);
    setMounted(true);
  }, []);

  // Apply theme changes
  useEffect(() => {
    if (mounted) {
      applyTheme(theme);
    }
  }, [theme, mounted]);

  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'light' ? 'dark' : 'light');
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, mounted }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
} 