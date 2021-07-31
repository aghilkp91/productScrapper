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
    name = "revitsport"
    COMPANY = "REVIT"
    start_urls = []
    img_utils = imageUtils.ImageUtils()

    def __init__(self):
        super().__init__(self.COMPANY, self.name)
    
    def getItemCategory(self, item_category_in, response):
        try:
            item_category = response.meta['result'].itemCategory
            return item_category
        except Exception as exp:
            logger.error(exp)
            return None

    def getGender(self, gender_in, response):
        try:
            gender = response.meta['result'].gender
            return gender
        except Exception as exp:
            logger.error(exp)
            return None

    def getColor(self, color_in, response):
        try:
            color_arr = []
            product_name = response.xpath("//*[@id='product-addtocart-button']/@data-name").get().lower().split( )[-1]
            for url in response.xpath("//a[contains(@class,'product-item-photo')]/@href"):
                color_arr.append(url.get().split(product_name)[-1].replace("-"," ").strip())
            color = ' || '.join(color_arr)
            color = (color[:253] + '..') if len(color) > 255 else color
            if not color:
                color = None
            return color
        except Exception as exp:
            logger.error(exp)
            return None

    def getSize(self, size_in, response):
        try:
            size = ' || '.join(map(lambda x:x.get().strip(), response.xpath('//div[contains(@id,"product-options")]/div//tr/td[1]/text()')))
            size = (size[:253] + '..') if len(size) > 255 else size
            if not size:
                size = None
            return size
        except Exception as exp:
            logger.error(exp)
            return None
    

    def getOriginalCompanyName(self, companyName, response):
        return "REVIT"

    def getImageOriginalUrl(self, imageOriginalUrl_after_strip, response):
        try:
            return imageOriginalUrl_after_strip.split('?')[0].strip()
        except Exception as exp:
            logger.error(exp)
            return None

    def parse(self, response):
       
        print(response.meta['productId'])

        self.xpath_dicts = {
            # 'gender': gender,
            'itemName': "//*[@id='product-addtocart-button']/@data-name",
            # 'itemCategory': '//nav[@data-section-type="Navigation"]/ol/li[last()]/meta/@content',
            'itemCategory': '/html/head/script[6]/text()',
            'itemNumber': '//div[@class="product-code"]/text()',
            # 'originalCompanyName': '//a[contains(@class,"product-show-details-name")]/text()',
            # 'image': '//div[contains(@class,"product-show-media-image")]/meta/@content',
            'imageOriginalUrl': "//div[contains(@class,'gallery-placeholder')]//img/@src",
            'productRating': "//div[contains(@class,'product-rating__stars')]/@data-rating",
            'price': "//span[contains(@id,'product-price')]/@data-price-amount"
        }

        super().parse(response)

