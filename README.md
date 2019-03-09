# Guiamais Scraper
### A webscraper for the website Guia Mais.

This is a silly small project for a webscraper that's able to extract query information from the brazilian website 'Guia Mais'.
It's fairly simple, it parses the html for a query and fetches the data and outputs to a .csv in a formatted way (at least I tried to.. ok? Some query results are weird and they give us a bit of a hard time lol)

There's a slight problem that I noticed afterwards: some queries depend on the website JS to load (which is quite stupid if you ask me), so these aren't included in the .csv since requests only parses the default html. Those results can be easily identified: they have stars (review stars).

To run this you'll need BeautifulSoup so run:
   
   ```shell
   pip3 install BeautifulSoup
   ```
