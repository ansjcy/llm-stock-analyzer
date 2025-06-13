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
        const timestamp = `${date}_${time}`;

        if (!reportGroups[ticker]) {
          reportGroups[ticker] = {
            ticker,
            date,
            time,
            timestamp,
            baseFile: null,
            llmFile: null,
            hasComplete: false,
            allFiles: []
          };
        }

        // Store all files for this ticker
        reportGroups[ticker].allFiles.push({
          filename: file,
          fullPath: `${basePath}/reports/${file}`,
          date,
          time,
          timestamp,
          type
        });

        // Update group timestamp to latest
        if (timestamp > reportGroups[ticker].timestamp) {
          reportGroups[ticker].date = date;
          reportGroups[ticker].time = time;
          reportGroups[ticker].timestamp = timestamp;
        }
      }
      // Legacy files have been removed, only process base and LLM files
    });

    // Now process each ticker to find the best files (prefer files with data over latest timestamp)
    for (const ticker of Object.keys(reportGroups)) {
      const group = reportGroups[ticker];

      // Sort files by timestamp (latest first)
      group.allFiles.sort((a: any, b: any) => b.timestamp.localeCompare(a.timestamp));

      // Find the best base file (prefer files with actual data)
      let bestBaseFile = null;
      for (const file of group.allFiles.filter((f: any) => f.type === 'base')) {
        try {
          const filePath = path.join(process.cwd(), 'public', 'reports', file.filename);
          const fileContent = await fs.readFile(filePath, 'utf8');
          const fileData = JSON.parse(fileContent);

          // Check if this file has meaningful data
          const hasValidStockInfo = fileData.stock_info && (
            fileData.stock_info.current_price ||
            fileData.stock_info.market_cap ||
            fileData.stock_info.name
          );

          const hasValidTechnicalAnalysis = fileData.technical_analysis && (
            fileData.technical_analysis.overall_signal ||
            fileData.technical_analysis.moving_averages ||
            fileData.technical_analysis.momentum
          );

          if (hasValidStockInfo || hasValidTechnicalAnalysis) {
            bestBaseFile = file;
            break; // Use the first (latest) file with valid data
          }
        } catch (error) {
          console.error(`Error reading file ${file.filename}:`, error);
        }
      }

      // If no file with data found, use the latest file anyway
      if (!bestBaseFile) {
        bestBaseFile = group.allFiles.find((f: any) => f.type === 'base');
      }

      // Find the latest LLM file (timestamp-based since LLM files are usually smaller)
      const latestLlmFile = group.allFiles.find((f: any) => f.type === 'llm');

      if (bestBaseFile) {
        group.baseFile = {
          filename: bestBaseFile.filename,
          fullPath: bestBaseFile.fullPath,
          date: bestBaseFile.date,
          time: bestBaseFile.time
        };

        // Update group timestamp to match the selected base file
        group.date = bestBaseFile.date;
        group.time = bestBaseFile.time;
      }

      if (latestLlmFile) {
        group.llmFile = {
          filename: latestLlmFile.filename,
          fullPath: latestLlmFile.fullPath,
          date: latestLlmFile.date,
          time: latestLlmFile.time
        };
      }

      // Check if we have both files
      group.hasComplete = !!(group.baseFile && group.llmFile);

      // Clean up temporary data
      delete group.allFiles;
      delete group.timestamp;
    }

    // Convert to array (validation already done during file selection)
    const validReports = Object.values(reportGroups).filter((group: any) => group.baseFile);

    // Sort by date/time (latest first)
    const reports = validReports.sort((a: any, b: any) => {
      if (a.date !== b.date) return b.date.localeCompare(a.date);
      return b.time.localeCompare(a.time);
    });

    return NextResponse.json({ reports });
  } catch (error) {
    console.error('Error reading reports directory:', error);
    return NextResponse.json({ error: 'Failed to load reports' }, { status: 500 });
  }
} 