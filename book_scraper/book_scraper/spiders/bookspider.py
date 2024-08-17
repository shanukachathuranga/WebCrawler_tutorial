import scrapy


class BookspiderSpider(scrapy.Spider):
    name = "bookspider" # Name of the spider,  $ scrapy crawl bookspider
    allowed_domains = ["books.toscrape.com"] # Allowed domains to scrape
    start_urls = ["https://books.toscrape.com"] # URL to start scraping


    # Method to parse the response from the start_urls and extract the data 
    # we need from the page
    def parse(self, response):
        books = response.css('article.product_pod')
        for book in books:
            relative_url = book.css('h3 a::attr(href)').get()

            if 'catalogue/' not in relative_url:
                book_url = 'https://books.toscrape.com/catalogue/'+ relative_url
            else:
                book_url = 'https://books.toscrape.com/'+ relative_url
            yield response.follow(book_url, callback=self.parse_book_page)

        next_page = response.css('.next a::attr(href)').get()
        if next_page is not None:
            if 'catalogue/' not in next_page:
                next_page = 'https://books.toscrape.com/catalogue/'+ next_page
            else:
                next_page = 'https://books.toscrape.com/'+ next_page 
            yield response.follow(next_page, callback=self.parse)

        
    def parse_book_page(self, response):
        table_rows = response.css('table tr')

        yield{
            'url': response.url,
            'title': response.css('.product_main h1::text').get(),
            'product_type': table_rows[1].css('td::text').get(),
            'price_excl_tax': table_rows[2].css('td::text').get(),
            'price_incl_tax': table_rows[3].css('td::text').get(),
            'tax': table_rows[4].css('td::text').get(),
            'availability': table_rows[5].css('td::text').get().split('(')[1].split(')')[0],
            'num_reviews': table_rows[6].css('td::text').get(),
            'stars': response.css('p.star-rating::attr(class)').get().split()[-1],
            'category': response.css('.breadcrumb li:nth-child(3) a::text').get(),
            'description': response.css('#product_description + p::text').get(),
            'price':response.css('.price_color::text').get()
        }