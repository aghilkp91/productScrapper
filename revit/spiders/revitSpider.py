import scrapy
import os
import Database.Database as Database
from scrapy.http import Request
from revit import imageUtils

class RevitSpider(scrapy.Spider):
    db, db_enigne = Database.initSession()
    img_utils = imageUtils.ImageUtils()

    def __init__(self, company, name):
        self.company_id = None
        self.name = name
        self.COMPANY = company

    def start_requests(self):
        session = self.db()
        companyUrl = session.query(Database.CompanyUrls). \
            filter_by(name=self.COMPANY).first()
        companyUrl_id = companyUrl.id
        self.company_id = companyUrl_id

        # # To crawl only one product
        result = session.query(Database.Products).filter(Database.Products.companyId == self.company_id,
                                                         Database.Products.isParsed == False).first()
        meta = {'productId': result.productId}
        yield Request(result.productUrl, dont_filter=True, meta=meta)

        # # To crawl entire products
        # result = session.query(Database.Products).filter(Database.Products.companyId == self.company_id,
        #                                                  Database.Products.isParsed == False).all()
        # for res in result:
        #     # self.start_urls.append(res.url)
        #     meta = {'productId': res.productId}
        #     yield Request(res.productUrl, dont_filter=True)

    def get_image(self, response, image_url, id):
        image_name = id + '.' + image_url.split(".")[-1]
        downloaded_image = imageUtils.ImageUtils.downloadImage(self.img_utils, image_url, image_name)
        uploaded_image = imageUtils.ImageUtils.uploadImage(self.img_utils, downloaded_image, image_name)
        os.remove(downloaded_image)
        return uploaded_image



