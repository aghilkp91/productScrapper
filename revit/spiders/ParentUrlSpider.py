import scrapy
import Database.Database as Database
from scrapy import signals
import logging

logger = logging.getLogger(__name__)

class RevitUrlSpider(scrapy.Spider):
    """ This is the base class which needs to inherited in the child class we create for all product url spiders

        This class overwrites spider_opened() and from_crawler() functions from the Scrapy.Spider class.

        This class get the starting urls from the DB according to the COMPANY name given and start crawling one by one.

        The spiders runs for the company initialized in the init function. So make sure COMPANY is initialized in the child function. 
        This company name is used to get company id from the CompanyUrls Table which is used to start the crawling of data

        You need to create a child class and overwrite the parse function to get the product urls and perform pagination.

    """


    db, db_enigne = Database.initSession()

    def __init__(self, company, name, total_products_per_page):
        self.company_id = None
        self.name = name
        self.COMPANY = company
        self.TOTAL_PRODUCTS_PER_PAGE = total_products_per_page

    def spider_opened(self):
        """
        This is an over written function of base spider class

        This function initializes db and then find the company id from CompanyUrls Table. This id is used to find all the category urls. 
        Then web crawler will run for all the category URLs.
        """
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
        """
        This is an over written function of base spider class

        This function calls the singal function to start the crawler and pass the spider variable.
        """
        spider = super(RevitUrlSpider, cls).from_crawler(crawler, *args, **kwargs)
        # spider.start_urls = cls.get_urls_from_db()
        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
        return spider
