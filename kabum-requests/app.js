const fs = require('fs');
const pageScraper = require('./pageScraper');

(async () => {
    try {
        fs.readFile('config.json', async (err, data) => {
            if (err) {
                throw err;
            }

            const config = JSON.parse(data);
            const kabumUrl = 'https://www.kabum.com.br'

            let promises = [];

            for (filter of config.filters) {
                for (let i = 0; i < config.maxPages; i++) {
                    let fullUrl = kabumUrl + '/' + filter + '?pagina=' + i;
                    promises.push(pageScraper({fullUrl, config}));
                }
            }

            const results = await Promise.all(promises);
            fs.writeFileSync('results.json', JSON.stringify(results, null, 4));
        });
    } catch (e) {
        console.log('Error', e);
    }
})();