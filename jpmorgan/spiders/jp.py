import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from jpmorgan.items import Article


class JpSpider(scrapy.Spider):
    name = 'jp'
    start_urls = ['https://www.jpmorgan.com/news']

    def parse(self, response):
        links = response.xpath('//div[@class="title"]/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1[@class="article__body__head"]/text()').get()
        if title:
            title = title.strip()
        else:
            return
        date = response.xpath('(//span[@class="article__body__text--bold"])[last()]/text()').get()
        if date:
            date = datetime.strptime(date.strip(), '%b %d, %Y')
            date = date.strftime('%Y/%m/%d')

        content = response.xpath('(//div[@class="cmp-text "])[1]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
