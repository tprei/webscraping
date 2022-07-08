import axios from 'axios'
import cheerio from 'cheerio'
import { Response } from 'express'

interface scrapable {
    where: string
    what: string
    lastPage: string
}

interface result {
    name: string
    address: string
    city: string
    state: string
    postalCode: string
    phones: string[]
    type: string
}

const defaultHeaders = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
    'cookie': 'niceUrl=sao-paulo-sp; AWSELB=replaced'
}

const baseURL = 'https://www.guiamais.com.br'
const searchURL = baseURL + '/encontre?searchbox=true'
const paginationSelector = '.pagination > a'

const merchantCardSelector = '.aTitle > a'
const merchantNameSelector = '.tp-companyName'

const merchantAddressSelector = '.tp-address'
const merchantCitySelector = '.tp-city'
const merchantStateSelector = '.tp-state'
const merchantPostalSelector = '.tp-postalCode'
const merchantTypeSelector = '.tp-category'

const merchantPhonesSelector = '.tp-phone'

class Scraper {
    initialTargets: Promise<scrapable>[] = []
    results: result[] = []

    constructor(cities: string[], queries: string[]) {
        this.setup(cities, queries)
    }

    private setup(cities: string[], queries: string[]) {
        // generate page URLs
        cities.forEach(async city => {
            queries.forEach(async query => {
                city = city.trim().replaceAll(' ', '')
                query = query.trim().replaceAll(' ', '')

                const lastPageURL = `${searchURL}&what=${query}&where=${city}&page=9999`

                this.initialTargets.push(
                    axios.get(lastPageURL)
                        .then((resp) => {
                            const $ = cheerio.load(resp.data)

                            // get number pages for current (city, query)
                            const lastPage = $(paginationSelector).last().text().trim()
                            return {
                                what: query,
                                where: city,
                                lastPage: lastPage,
                            } as scrapable
                        }).catch((err: string) => {
                            console.error(`error occured getting pages for query "${query}", city "${city}": ${err}`)
                            return { what: '', where: '', lastPage: '' } as scrapable
                        })
                )
            })
        })
    }

    run(res: Response) {
        let output = 'Página, Nome, Endereço, Cidade, Estado, CEP, Tipo, Telefones<br/>'
        let promises: Promise<result[][]>[] = this.initialTargets.map(async (target) => {
            return target.then(async (result) => {
                let promises = []
                for (let i = 1; i <= parseInt(result.lastPage); i++) {
                    const pageNumber = i.toString()
                    const resultsURL = `${searchURL}&what=${result.what}&where=${result.where}&page=${pageNumber}`

                    promises.push(
                        axios.get(resultsURL, {
                            headers: defaultHeaders
                        }).then(resp => {
                            // get results page
                            const $ = cheerio.load(resp.data)
                            const results = $(merchantCardSelector)

                            let merchantPromises = []

                            for (let i = 0; i < results.length; i++) {
                                const merchantURL = baseURL + results.eq(i).attr('href')
                                merchantPromises.push(
                                    axios.get(
                                        merchantURL,
                                        { headers: defaultHeaders }
                                    ).then(resp => {
                                        const $ = cheerio.load(resp.data)

                                        const name = $(merchantNameSelector).text().trim()
                                        const address = $(merchantAddressSelector).text().trim()

                                        const city = $(merchantCitySelector).text().trim()
                                        const state = $(merchantStateSelector).text().trim()
                                        const postalCode = $(merchantPostalSelector).text().trim()
                                        const type = $(merchantTypeSelector).text().trim()

                                        const phones = $(merchantPhonesSelector)

                                        let entryPhones = []
                                        for (let i = 0; i < phones.length; i++) {
                                            entryPhones.push(phones.eq(i).text().trim())
                                        }

                                        const entry: result = {
                                            name: name,
                                            address: address.replace(/\s{2,}/g, ''),
                                            city: city,
                                            state: state,
                                            postalCode: postalCode,
                                            phones: entryPhones,
                                            type: type
                                        }

                                        return entry
                                    })
                                )
                            }

                            return Promise.all(merchantPromises)
                        })
                    )
                }

                return Promise.all(promises)
            })
        })

        Promise.all(promises).then((tuples) => {
            tuples.forEach(
                (city) => {
                    city.forEach(
                        query => query.forEach(
                            row => {
                                //'Nome, Endereço, Cidade, Estado, CEP, Tipo, Telefones<br/>'
                                output += `${row.name}, ${row.address}, ${row.city}, ${row.state}, ${row.postalCode}, ${row.type}, ${row.phones}<br/>`
                            }
                        )
                    )
                }
            )

            res.send(output)
        })

    }
}

export default Scraper