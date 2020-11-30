import scrapy
import Database.Database as Database
from scrapy import signals
import logging

logger = logging.getLogger(__name__)

class RevitUrlSpider(scrapy.Spider):
    db, db_enigne = Database.initSession()

    def __init__(self, company, name, total_products_per_page):
        self.company_id = None
        self.name = name
        self.COMPANY = company
        self.TOTAL_PRODUCTS_PER_PAGE = total_products_per_page

    def spider_opened(self):
        session = self.db()
        companyUrl = session.query(Database.CompanyUrls). \
            filter_by(name=self.COMPANY).first()
        self.company_id = companyUrl.id
        result = session.query(Database.CategoryUrls).filter_by(companyId=self.company_id).all()

        for res in result:
            logger.debug("Reulting url form DB : %s" %res.url)
            self.start_urls.append(res.url)

        print(self.start_urls)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(RevitUrlSpider, cls).from_crawler(crawler, *args, **kwargs)
        # spider.start_urls = cls.get_urls_from_db()
        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
        return spider
