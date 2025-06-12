const open = require('open');
const path = require('path');

// Wait for coverage report generation
setTimeout(async () => {
    try {
        const coveragePath = path.resolve(__dirname, 'coverage/extract-load-ui/index.html');
        console.log('\nOpening coverage report at:', coveragePath);
        await open(coveragePath);
    } catch (err) {
        console.error('Error opening coverage report:', err);
    }
}, 3000);