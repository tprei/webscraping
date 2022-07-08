import express from 'express'
import { unlink, unlinkSync } from 'fs'
import Scraper from "./scraper"

const app = express()
const port = 8000

app.use(
    express.static('public')
)

app.get('/scrape', (req, res) => {
    console.log(req.query)

    try {
        const city = req.query['city'] as string
        const query = req.query['query'] as string
        const scraper = new Scraper(city.split('\n'), query.split('\n'))
        scraper.run(res)
    } catch (err) {
        console.error('failed to scrape with given query')
    }
})

app.listen(8000)
console.log('listening on', port)
