import scrapy
import re
import Database.Database as Database
from revit.spiders import revitSpider

class IxonProductsSpider(revitSpider.RevitSpider):
    db, db_enigne = Database.initSession()
    name = "ixon"
    COMPANY = "Ixon"
    start_urls = []

    def __init__(self):
        super().__init__(self.COMPANY, self.name)

    def parse(self, response):
        session = self.db()

        itemName = response.xpath('//section[contains(@class,"type-product")]//span/text()').get()
        # itemNumber = response.xpath('//div[contains(@class,"product-upc")]/span/text()').get().strip()
        price = response.xpath('//div[contains(@class,"wpb_content_element")]/div/p/span/strong/text()').get()
        itemCategory = response.xpath('//*[@id="content"]/div/section/@class').get().split('pa_vetements-')[-1].split(" ")[0]
        color = '||'.join(map(lambda x:x.get().strip(), response.xpath('//div[contains(@class,"wpb_content_element")]/div/p/span/span/text()')))
        size = '||'.join(map(lambda x:x.get().strip(), response.xpath('//div[contains(@class,"wpb_content_element")]/div/p/strong/span/span/text()')))
        gender = response.xpath('//*[@id="content"]/div/section/@class').get().split('pa_genre-')[-1].split(" ")[0]
        # image
        print(response.meta['productId'])
        dicts = {
            'itemName': itemName,
            'itemCategory': itemCategory,
            # 'itemNumber': itemNumber,
            'price': price,
            'color': color,
            'size': size,
            'gender': gender,
            'isParsed': True
        }

        session.query(Database.Products).filter_by(productId=response.meta['productId']).update(dicts)
        session.commit()

