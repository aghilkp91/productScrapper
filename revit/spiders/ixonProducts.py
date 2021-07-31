import scrapy
import re
import Database.Database as Database
from revit.spiders import ParentSpider
from revit import imageUtils

class IxonProductsSpider(ParentSpider.RevitSpider):
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
        price_str = response.xpath('//div[contains(@class,"wpb_content_element")]/div/p/span/strong/text()').get()
        price = re.findall('\d+.\d+', price_str)[0] if price_str else None
        item_category_in = response.xpath('//*[@id="content"]/div/section/@class').get().split('pa_vetements-')[-1].split(" ")[0]
        item_category = self.get_category(item_category_in)
        item_style_in = response.xpath('//div[contains(@class,"p-responsive")]//div//p//text()').get()
        item_style = self.get_styles(item_style_in)
        color = '||'.join(map(lambda x:x.get().strip(), response.xpath('//div[contains(@class,"wpb_content_element")]/div/p/span/span/text()')))
        color = (color[:253] + '..') if len(color) > 255 else color
        size = '||'.join(map(lambda x:x.get().strip(), response.xpath('//div[contains(@class,"wpb_content_element")]/div/p/strong/span/span/text()')))
        size = (size[:253] + '..') if len(size) > 255 else size
        gender = response.xpath('//*[@id="content"]/div/section/@class').get().split('pa_genre-')[-1].split(" ")[0]
        gender = None if gender == "$classes" else gender
        image_url = response.xpath('//*[@id="content"]//section/div[1]//img/@data-lazy-src').get()
        upload_image_path = self.get_image(response, image_url, response.meta['productId'])
        print(response.meta['productId'])
        dicts = {
            'itemName': item_name,
            'itemCategory': item_category,
            'originalCompanyName': self.COMPANY,
            # 'itemNumber': itemNumber,
            'price': price,
            'color': color,
            'size': size,
            'gender': gender,
            'image': upload_image_path,
            'imageOriginalUrl': image_url,
            'isParsed': True
        }

        if item_style:
            dicts['itemStyle'] = item_style

        session.query(Database.Products).filter_by(productId=response.meta['productId']).update(dicts)
        session.commit()

