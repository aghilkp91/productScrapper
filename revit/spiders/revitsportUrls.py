import scrapy
import uuid
import re
import Database.Database as Database
from revit.spiders import ParentUrlSpider
import logging

logger = logging.getLogger(__name__)

class RevitsportUrlsSpider(ParentUrlSpider.RevitUrlSpider):
    db, db_enigne = Database.initSession()
    company_id = None
    start_urls = []
    name = "revitsportUrls"
    COMPANY = "REVIT"
    TOTAL_PRODUCTS_PER_PAGE = 12

    def __init__(self):
        super().__init__(self.COMPANY, self.name, self.TOTAL_PRODUCTS_PER_PAGE)

    def parse(self, response):
        session = self.db()
        reviewids_results = session.query(Database.Products.productId).filter(Database.Products.companyId == self.company_id).all()
        review_ids = [ item[0] for item in reviewids_results ]
        # finding urls
        lists = []
        update_lists = []
        # logger.info("Starting crawling of %s" % response.url)
        print("Starting crawling of %s" % response.url)
        for url in response.xpath("//li//div[@class='label-container']/a/@href"):
            productUrl = url.get()
            productId = uuid.uuid3(uuid.NAMESPACE_URL, productUrl).hex
            companyId = self.company_id
            try:
                category = response.url.split('?')[0].split('/')[-1].capitalize()
            except Exception as exp:
                logger.error(exp)
                category = None
            try:
                gender = response.url.split('?')[0].split('/')[-2].capitalize()
            except Exception as exp:
                logger.error(exp)
                gender = None

            if productId in review_ids:
                dicts = {'productId': productId, 'isParsed': False}
                update_lists.append(dicts)
            else:
                dicts = {'productUrl': productUrl, 'productId': productId, 'companyId': companyId, 'isParsed': False, 'itemCategory': category, 'gender': gender }
                lists.append(dicts)
        # print(dicts)
        # filename = 'revit/spiders/temp/-%s.txt' % page_name
        # with open(filename, 'a') as f:
        #     f.write(str(lists))
        if (len(lists) > 0):
            session.bulk_insert_mappings(Database.Products, lists)
            session.commit()
        if (len(update_lists) > 0):
            session.bulk_update_mappings(Database.Products, update_lists)
            session.commit()

        # Finding total products in page
        try:
            next_page = response.xpath("//li[contains(@class,'pages-item-next')]/a/@href").get()
            print("Next page %s" %next_page)
            if next_page:
                yield scrapy.Request(next_page, callback=self.parse)
        except Exception as exp:
            logger.error(exp)
