import scrapy
import re
from Database import Database
from revit.spiders import ParentSpider

class AlphineStarsSpider(ParentSpider.RevitSpider):
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
        price_str = response.xpath('//span[@class="money"]/text()').get().strip()
        price = re.findall('\d+.\d+', price_str)[0]
        try:
            originalPriceStr = response.xpath('//div[@class="price--main"]/span[@class="money"]/text()')
            originalPrice = re.findall('\d+.\d+', originalPriceStr)[0]
        except Exception as exp:
            logger.warning(exp)

        for script in response.xpath("//script/text()"):
            # m = re.findall('collection_count', script.get())
            m = re.search('"type":"(.+?)","variants"', script.get())
            if m:
                # m = re.search('collection_count: (.+?),', script.get())
                inp_itemCategory=m.group(1)
                break
        itemCategory = self.get_category(inp_itemCategory)
        inpItemStyle = response.xpath('//*[@id="shopify-section-static-product"]/nav/a[2]/text()').get()
        itemStyle = self.get_styles(inpItemStyle)
        color = '||'.join(map(lambda x:x.get().strip(), response.xpath('//*[contains(@id,"product_form")]/div[1]/fieldset[2]/div/div/label/input/@value')))
        color = (color[:253] + '..') if len(color) > 255 else color

        size = '||'.join(map(lambda x:x.get().strip(), response.xpath('//*[contains(@id,"product_form")]/div[1]/fieldset[1]/div/div/label/input/@value')))
        size = (size[:253] + '..') if len(size) > 255 else size
        gender = 'Women' if re.search('women', itemName.lower()) else 'Men'
        # image
        image_url = 'https:' + response.xpath('//div[contains(@class,"product-gallery")]/img/@src').get().split('?')[0]
        upload_image_path = self.get_image(response, image_url, response.meta['productId'])
        print(response.meta['productId'])
        dicts = {
            'itemName': itemName,
            'itemCategory': itemCategory,
            'itemStyle': itemStyle,
            'itemNumber': itemNumber,
            'originalCompanyName': self.COMPANY,
            'price': price,
            'color': color,
            'size': size,
            'gender': gender,
            'image': upload_image_path,
            'imageOriginalUrl': image_url,
            'isParsed': True
        }

        if itemStyle:
            dicts['itemStyle'] = itemStyle
        if originalPrice:
            dicts['originalPrice'] = originalPrice

        session.query(Database.Products).filter_by(productId=response.meta['productId']).update(dicts)
        session.commit()

