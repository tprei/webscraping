const pageScraper = require('./pageScraper')

async function scrape (product, {browser, config}) {

    let allProducts = [];

    for (let i = 1; i <= config.maxPages; i++) {
        const URL = config.root_url + product + '?pagina=' + i;
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

    return allProducts;
}

exports.start = (async (browser, config) => {
    let results = {};
    let totalResults = 0;
    let promises = config.filters.map(filter => scrape(filter, {browser, config}));
    let allResults = await Promise.all(promises);

    for (const l of allResults) {
        totalResults += l.length;
    }

    console.log(totalResults);
    return allResults;
});