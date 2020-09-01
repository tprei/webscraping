const pageScraper = require('./pageScraper')

exports.start = (async (browser, config) => {
    let results = {};
    for (const p of config.filters) {
        let allProducts = [];
        for (let i = 1; i <= config.maxPages; i++) {

            const URL = config.root_url + p + '?pagina=' + i;

            const page = await browser.newPage();
            await page.setUserAgent(config.userAgent);
            await page.goto(URL);

            products = await pageScraper.scrape(page);
            allProducts = allProducts.concat(products);

            if (allProducts.length === 0) {
                break;
            }
        }
        results[p] = allProducts;
    }

    console.log(results);

});