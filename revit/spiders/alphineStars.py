import scrapy
import re
import Database.Database as Database
from revit.spiders import revitSpider

class AlphineStarsSpider(revitSpider.RevitSpider):
    db, db_enigne = Database.initSession()
    name = "alpineStars"
    COMPANY = "Alpinestars"
    start_urls = []

    def __init__(self):
        super().__init__(self.COMPANY, self.name)

    def parse(self, response):
        session = self.db()

        itemName = response.xpath('//h1[@class="product-title"]/text()').get().strip()
        itemNumber = response.xpath('//div[contains(@class,"product-upc")]/span/text()').get().strip()
        price = response.xpath('//span[@class="money"]/text()').get().strip()
        itemCategory = response.xpath('//*[@id="shopify-section-static-product"]/nav/a[2]/text()').get()
        color = '||'.join(map(lambda x:x.get().strip(), response.xpath('//*[contains(@id,"product_form")]/div[1]/fieldset[2]/div/div/label/input/@value')))
        size = '||'.join(map(lambda x:x.get().strip(), response.xpath('//*[contains(@id,"product_form")]/div[1]/fieldset[1]/div/div/label/input/@value')))
        gender = 'Women' if re.search('women', itemName.lower()) else 'Men'
        # image
        image_url = 'https:' + response.xpath('//div[contains(@class,"product-gallery")]/img/@src').get().split('?')[0]
        upload_image_path = self.get_image(response, image_url, response.meta['productId'])
        print(response.meta['productId'])
        dicts = {
            'itemName': itemName,
            'itemCategory': itemCategory,
            'itemNumber': itemNumber,
            'price': price,
            'color': color,
            'size': size,
            'gender': gender,
            'image': upload_image_path,
            'isParsed': True
        }

        session.query(Database.Products).filter_by(productId=response.meta['productId']).update(dicts)
        session.commit()

