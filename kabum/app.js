const fs = require('fs')
const puppeteer = require('puppeteer');
const scraper = require('./scraper');

function loadConfig(file) {
    const configFile = fs.readFileSync(file);
    return JSON.parse(configFile);
}

module.exports = (async () => {
    const configFile = loadConfig('config.json');
    const browser = await puppeteer.launch({headless: configFile.headless});

    await scraper.start(browser, configFile);
})();