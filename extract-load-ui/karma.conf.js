module.exports = function (config) {
  config.set({
    // ...existing code...
    coverageReporter: {
      dir: require('path').join(__dirname, './coverage'),
      subdir: '.',
      reporters: [
        { type: 'html' },
        { type: 'text-summary' }
      ]
    },
    reporters: ['progress', 'coverage'],
    // ...existing code...
  });
};