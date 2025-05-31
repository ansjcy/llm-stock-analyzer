#!/usr/bin/env node

const fs = require('fs').promises;
const path = require('path');

async function syncReports() {
  const sourceDir = path.join(process.cwd(), '..', 'reports');
  const targetDir = path.join(process.cwd(), 'public', 'reports');

  try {
    // Ensure target directory exists
    await fs.mkdir(targetDir, { recursive: true });

    // Read source directory
    const files = await fs.readdir(sourceDir);
    const jsonFiles = files.filter(file => file.endsWith('.json'));

    console.log(`Found ${jsonFiles.length} JSON reports in source directory`);

    let copiedCount = 0;
    let skippedCount = 0;

    for (const file of jsonFiles) {
      const sourcePath = path.join(sourceDir, file);
      const targetPath = path.join(targetDir, file);

      try {
        // Check if target file already exists and compare timestamps
        const sourceStats = await fs.stat(sourcePath);
        
        try {
          const targetStats = await fs.stat(targetPath);
          if (targetStats.mtime >= sourceStats.mtime) {
            console.log(`⏭️  Skipping ${file} (already up to date)`);
            skippedCount++;
            continue;
          }
        } catch (error) {
          // Target file doesn't exist, proceed with copy
        }

        await fs.copyFile(sourcePath, targetPath);
        console.log(`✅ Copied ${file}`);
        copiedCount++;
      } catch (error) {
        console.error(`❌ Error copying ${file}:`, error.message);
      }
    }

    console.log(`\n📊 Sync complete: ${copiedCount} copied, ${skippedCount} skipped`);
  } catch (error) {
    console.error('Error syncing reports:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  syncReports();
}

module.exports = syncReports; 