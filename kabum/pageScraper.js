exports.scrape = (async (page) => {

    // Get all products in this page
    const productList = await page.$$('#listagem-produtos  div .eITELq');

    // Nothing was found
    if (productList.length === 0) {
        console.log(`All results scraped on page ${await page.title()}`);
        return null;
    }

    let products = [];

    for (const p of productList) {
        const nameElement = await p.$('.item-nome');
        const nameText = await page.evaluate(name => name.innerText, nameElement);

        const creditElement = await p.$('.ksiZrQ');
        const creditText = await page.evaluate(credit => credit.innerText, creditElement);

        const boletoElement = await p.$('.qatGF');
        const boletoText = await page.evaluate(boleto => boleto.innerText, boletoElement);

        products.push({nameText, creditText, boletoText});
    }

    return products;

});