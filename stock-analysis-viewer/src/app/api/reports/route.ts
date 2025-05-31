import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

export const dynamic = 'force-static';
export const revalidate = false;

export async function GET() {
  try {
    const reportsDir = path.join(process.cwd(), 'public', 'reports');
    
    // Check if reports directory exists
    try {
      await fs.access(reportsDir);
    } catch {
      return NextResponse.json({ reports: [] });
    }
    
    const files = await fs.readdir(reportsDir);
    const jsonFiles = files.filter(file => file.endsWith('.json'));
    
    const reports = jsonFiles.map(file => {
      const match = file.match(/^([A-Z]+)_analysis_(\d+)_(\d+)\.json$/);
      if (match) {
        const ticker = match[1];
        const date = match[2];
        const time = match[3];
        return {
          filename: file,
          ticker,
          date,
          time,
          fullPath: `/reports/${file}`
        };
      }
      return {
        filename: file,
        ticker: file.split('_')[0] || 'UNKNOWN',
        date: 'unknown',
        time: 'unknown',
        fullPath: `/reports/${file}`
      };
    });
    
    return NextResponse.json({ reports });
  } catch (error) {
    console.error('Error reading reports directory:', error);
    return NextResponse.json({ error: 'Failed to load reports' }, { status: 500 });
  }
} 