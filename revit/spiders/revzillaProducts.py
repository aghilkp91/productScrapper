import scrapy
import re
import Database.Database as Database
from revit.spiders import ParentSpider
from revit import imageUtils
import logging
import json

logger = logging.getLogger(__name__)
class RevzillaProductsSpider(ParentSpider.RevitSpider):
    db, db_enigne = Database.initSession()
    name = "revzilla"
    COMPANY = "Revzilla"
    start_urls = []
    img_utils = imageUtils.ImageUtils()

    def __init__(self):
        super().__init__(self.COMPANY, self.name)


    def getPrice(self, price_str, response):
        try:
            price_str = response.xpath('//div[contains(@class,"price-retail")]/span/span/text()').get()
            price_ext = response.xpath('//div[contains(@class,"price-retail")]/span//sup[2]/text()').get()
            price = price_str + '.' + price_ext
            return price
        except Exception as exp:
            logger.error(exp)
            return None

    def getItemNumber(self, item_number_str, response):
        try:
            itemNumber = item_number_str.split(":")[-1].strip()
            return itemNumber
        except Exception as exp:
            logger.error(exp)
            return None
    
    # def getItemCategory(self, item_category_in, response):
    #     try:
    #         item_category = self.get_category(item_category_in)
    #         return item_category
    #     except Exception as exp:
    #         logger.error(exp)
    #         return None
    def getItemCategory(self, item_category_in, response):
        try:
            json_values = json.loads(item_category_in)
            item_category_i = json_values[0]['category'].split('>')[-1].strip().lower()
            item_category = self.get_category(item_category_i)
            return item_category
        except Exception as exp:
            logger.error(exp)
            return None

    def getColor(self, color_in, response):
        try:
            color = '||'.join(map(lambda x:x.get().strip(), response.xpath('//div[contains(@class,"option-type__swatches")]/input/@aria-label')))
            color = (color[:253] + '..') if len(color) > 255 else color
            if not color:
                color = None
            return color
        except Exception as exp:
            logger.error(exp)
            return None

    def getSize(self, size_in, response):
        try:
            size = '||'.join(map(lambda x:x.get().strip(), response.xpath('//select[@aria-label="Size"]/option/@data-label')))
            size = (size[:253] + '..') if len(size) > 255 else size
            if not size:
                size = None
            return size
        except Exception as exp:
            logger.error(exp)
            return None

    # def getImage(self, image_url, response):
    #     try:
    #         upload_image_path = self.get_image(response, image_url, response.meta['productId'])
    #         return upload_image_path
    #     except Exception as exp:
    #         logger.error(exp)
    #         return None
    
    def getDiscountPercent(self, discountPercent_str, response):
        try:
            discountPercent = discountPercent_str.replace('%', '')
            return discountPercent
        except Exception as exp:
            logger.error(exp)
            return None

    def getItemStyle(self, itemStyle_after_strip, response):
        try:
            return response.xpath("/html/head/meta[18]/@content").get().split('riding-style-')[-1].split(',')[0]
        except Exception as exp:
            logger.error(exp)
            return None

    def parse(self, response):
       
        print(response.meta['productId'])

        self.xpath_dicts = {
            'itemName': "//h1/text()",
            # 'itemCategory': '//nav[@data-section-type="Navigation"]/ol/li[last()]/meta/@content',
            'itemCategory': '/html/head/script[6]/text()',
            'itemNumber': '//div[contains(@class,"product-show-details-ids")]/span/text()',
            'originalCompanyName': '//a[contains(@class,"product-show-details-name")]/text()',
            'image': '//div[contains(@class,"product-show-media-image")]/meta/@content',
            'imageOriginalUrl': '//div[contains(@class,"product-show-media-image")]/meta/@content',
            'originalPrice': "//div[contains(@class,'price-was-discount')]/div/span/text()",
            'discountPercent': "//span[contains(@class,'price-discount-percentage')]/text()",
            'productRating': "//div[contains(@class,'product-rating__stars')]/@data-rating"
        }

        super().parse(response)

