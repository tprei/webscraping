const pageScraper = require('./pageScraper')

exports.start = (async (browser, config) => {
    let pages = []

    for (const p of config.filters){
        const prodURL = config.root_url + p;
        const productPage = await browser.newPage();
        await productPage.goto(prodURL);

        pages.push(productPage);
    }

    for (const page of pages){
        products = await pageScraper.scrape(page);
    }
});