const got = require('got');

module.exports = 
    async ({fullUrl, config}) => {
        try {
            const response = await got(fullUrl, headers={'user-agent': config.userAgent});

            if (response.statusCode != 200) {
                return [];
            }

            const htmlString = response.body;
            
            let i = htmlString.search("listagemDados");

            if (i == -1) {
                return [];
            } else {
                // get to the first '['
                i += 16;
            }

            let result = "";
            let open = 0;

            do {
                result += htmlString[i];

                if (htmlString[i] == '[') {
                    open++;
                } else if (htmlString[i] == ']'){
                    open--;
                }
                
                i++;
            } while (open != 0 && i != htmlString.length);

            products = JSON.parse(result);
            return products;

        } catch (e) {
            console.log(e);
            return [];
        }
    }