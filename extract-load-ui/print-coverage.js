const path = require('path');

const coveragePath = path.resolve(__dirname, 'coverage', 'extract-load-ui', 'index.html');
const fileUrl = `file:///${coveragePath.replace(/\\/g, '/')}`;

console.log('\n');
console.log('='.repeat(80));
console.log('Coverage report is available at:');
console.log(fileUrl);
console.log('='.repeat(80));