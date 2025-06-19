// This script copies the latest backend coverage report to the public directory for HTTP access
const fs = require('fs');
const path = require('path');

function copyFile(src, dest) {
  if (fs.existsSync(src)) {
    fs.copyFileSync(src, dest);
    console.log(`Copied: ${src} -> ${dest}`);
  } else {
    console.warn(`File not found: ${src}`);
  }
}

// Backend coverage only
const backendSrc = path.resolve(__dirname, '..', 'htmlcov', 'index.html');
const backendDest = path.resolve(__dirname, 'public', 'backend-coverage.html');
copyFile(backendSrc, backendDest);
