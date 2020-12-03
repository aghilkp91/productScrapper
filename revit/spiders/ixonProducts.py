import scrapy
import re
import Database.Database as Database
from revit.spiders import revitSpider
from revit import imageUtils

class IxonProductsSpider(revitSpider.RevitSpider):
    db, db_enigne = Database.initSession()
    name = "ixon"
    COMPANY = "Ixon"
    start_urls = []
    img_utils = imageUtils.ImageUtils()

    def __init__(self):
        super().__init__(self.COMPANY, self.name)

    def parse(self, response):
        session = self.db()

        item_name = response.xpath('//section[contains(@class,"type-product")]//span/text()').get()
        # itemNumber = response.xpath('//div[contains(@class,"product-upc")]/span/text()').get().strip()
        price = response.xpath('//div[contains(@class,"wpb_content_element")]/div/p/span/strong/text()').get()
        item_category = response.xpath('//*[@id="content"]/div/section/@class').get().split('pa_vetements-')[-1].split(" ")[0]
        color = '||'.join(map(lambda x:x.get().strip(), response.xpath('//div[contains(@class,"wpb_content_element")]/div/p/span/span/text()')))
        size = '||'.join(map(lambda x:x.get().strip(), response.xpath('//div[contains(@class,"wpb_content_element")]/div/p/strong/span/span/text()')))
        gender = response.xpath('//*[@id="content"]/div/section/@class').get().split('pa_genre-')[-1].split(" ")[0]
        image_url = response.xpath('//*[@id="content"]//section/div[1]//img/@data-lazy-src').get()
        upload_image_path = self.get_image(response, image_url, response.meta['productId'])
        print(response.meta['productId'])
        dicts = {
            'itemName': item_name,
            'itemCategory': item_category,
            # 'itemNumber': itemNumber,
            'price': price,
            'color': color,
            'size': size,
            'gender': gender,
            'image': upload_image_path,
            'isParsed': True
        }

        session.query(Database.Products).filter_by(productId=response.meta['productId']).update(dicts)
        session.commit()

