const pageScraper = require('./pageScraper')

exports.start = (async (browser, config) => {
    let results = {};
    let totalResults = 0;
    for (const p of config.filters) {
        let allProducts = [];
        for (let i = 1; i <= config.maxPages; i++) {

            const URL = config.root_url + p + '?pagina=' + i;

            const page = await browser.newPage();
            await page.setUserAgent(config.userAgent);
            await page.goto(URL);

            products = await pageScraper.scrape(page);

            if (products === null) {
                await page.close();
                break;
            }

            allProducts = allProducts.concat(products);
            await page.close();
        }

        results[p] = allProducts;
        totalResults += allProducts.length;
    }

    console.log(totalResults);
    return results;
});