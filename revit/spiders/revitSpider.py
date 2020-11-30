import scrapy
import re
import Database.Database as Database
from scrapy.http import Request

class RevitSpider(scrapy.Spider):
    db, db_enigne = Database.initSession()

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


