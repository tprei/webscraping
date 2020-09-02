const got = require('got');

module.exports = 
    async ({fullUrl, config}) => {
        try {
            console.log(`Entering ${fullUrl}`);
            const response = await got(fullUrl, headers={'user-agent': config.userAgent})
            const htmlString = response.body;
            
            let i = htmlString.search("listagemDados");

            if (i === -1) {
                return [];
            } else {
                // get to the first '['
                i += 16;
            }

            let result = "";
            let open = 0;

            do {
                result += htmlString[i];

                if (htmlString[i] === '[') {
                    open++;
                } else if (htmlString[i] === ']'){
                    open--;
                }
                
                i++;
            } while (open != 0 && i != htmlString.length);

            console.log(`Leaving ${fullUrl}`);
            return JSON.parse(result)[0];

        } catch (e) {
            console.log(e.response.body);
        }
    }