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

    // Get basePath for production builds
    const basePath = process.env.NODE_ENV === 'production' ? '/llm-stock-analyzer' : '';

    // Group files by ticker and timestamp to get the latest for each ticker
    const reportGroups: { [key: string]: any } = {};

    jsonFiles.forEach(file => {
      // Match naming convention: TICKER_analysis_TYPE_TIMESTAMP.json (only base and llm files)
      const newMatch = file.match(/^([A-Z]+)_analysis_(base|llm)_(\d+)_(\d+)\.json$/);

      if (newMatch) {
        const ticker = newMatch[1];
        const type = newMatch[2]; // 'base' or 'llm'
        const date = newMatch[3];
        const time = newMatch[4];

        if (!reportGroups[ticker]) {
          reportGroups[ticker] = {
            ticker,
            date,
            time,
            baseFile: null,
            llmFile: null,
            hasComplete: false
          };
        }

        if (type === 'base') {
          reportGroups[ticker].baseFile = {
            filename: file,
            fullPath: `${basePath}/reports/${file}`,
            date,
            time
          };
        } else if (type === 'llm') {
          reportGroups[ticker].llmFile = {
            filename: file,
            fullPath: `${basePath}/reports/${file}`,
            date,
            time
          };
        }

        // Update group timestamp to latest
        if (date > reportGroups[ticker].date || (date === reportGroups[ticker].date && time > reportGroups[ticker].time)) {
          reportGroups[ticker].date = date;
          reportGroups[ticker].time = time;
        }

        // Check if we have both files
        reportGroups[ticker].hasComplete = !!(reportGroups[ticker].baseFile && reportGroups[ticker].llmFile);

      }
      // Legacy files have been removed, only process base and LLM files
    });

    // Convert to array and sort by date/time
    const reports = Object.values(reportGroups).sort((a: any, b: any) => {
      if (a.date !== b.date) return b.date.localeCompare(a.date);
      return b.time.localeCompare(a.time);
    });

    return NextResponse.json({ reports });
  } catch (error) {
    console.error('Error reading reports directory:', error);
    return NextResponse.json({ error: 'Failed to load reports' }, { status: 500 });
  }
} 