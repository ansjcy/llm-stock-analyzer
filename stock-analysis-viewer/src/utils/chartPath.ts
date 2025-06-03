/**
 * Utility function to resolve chart paths based on environment
 * This handles the difference between development and production chart paths
 */

export function resolveChartPath(originalPath: string): string {
  if (!originalPath) return '';
  
  // If the path already starts with /llm-stock-analyzer, remove it for development
  if (originalPath.startsWith('/llm-stock-analyzer/charts/')) {
    // In development, we want to serve from /charts/ directly
    // In production, the basePath will be automatically added by Next.js
    return originalPath.replace('/llm-stock-analyzer', '');
  }
  
  // If the path starts with /charts/, keep it as is
  if (originalPath.startsWith('/charts/')) {
    return originalPath;
  }
  
  // If the path doesn't start with /, add it
  if (!originalPath.startsWith('/')) {
    return `/charts/${originalPath}`;
  }
  
  return originalPath;
}

/**
 * Get the proper chart path for the current environment
 * @param chartName - The chart filename (e.g., "AAPL_technical_analysis_20250531_072740.png")
 * @returns The resolved chart path
 */
export function getChartPath(chartName: string): string {
  if (!chartName) return '';
  
  // Remove any existing path components and just use the filename
  const filename = chartName.split('/').pop() || chartName;
  
  // Return the path relative to the public directory
  return `/charts/${filename}`;
} 