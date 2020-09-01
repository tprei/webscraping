const fs = require('fs')
const puppeteer = require('puppeteer');
const scraper = require('./scraper');

module.exports = (async () => {
    try {
        fs.readFile('config.json', async (err, data) => {
            if (err){
                throw err;
            }
            const configFile = JSON.parse(data);
            const browser = await puppeteer.launch({headless: configFile.headless});
            const results = await scraper.start(browser, configFile);

            await browser.close();
            fs.writeFileSync('results.json', JSON.stringify(results, null, 4));
        });
    } catch (e) {
        console.log('Error', e);
    }
})();