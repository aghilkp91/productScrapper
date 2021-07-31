import scrapy
import uuid
import re
import Database.Database as Database
from revit.spiders import ParentUrlSpider
import logging

logger = logging.getLogger(__name__)

class IxonUrlSpider(ParentUrlSpider.RevitUrlSpider):
    db, db_enigne = Database.initSession()
    company_id = None
    start_urls = []
    name = "ixonUrls"
    COMPANY = "Ixon"
    TOTAL_PRODUCTS_PER_PAGE = 12

    def __init__(self):
        super().__init__(self.COMPANY, self.name, self.TOTAL_PRODUCTS_PER_PAGE)

    def parse(self, response):
        try:
            # finding urls
            session = self.db()
            reviewids_results = session.query(Database.Products.productId).filter(Database.Products.companyId == self.company_id).all()
            review_ids = [ item[0] for item in reviewids_results ]
            lists = []
            update_lists = []
            logger.info("Starting crawling of %s" % response.url)
            for url in response.xpath('//div[contains(@class,"mb-5")]/a/@href'):
                productUrl = url.get()
                productId = uuid.uuid3(uuid.NAMESPACE_URL, productUrl).hex
                companyId = self.company_id

                if productId in review_ids:
                    dicts = {'productId': productId, 'isParsed': False}
                    update_lists.append(dicts)
                else:
                    dicts = {'productUrl': productUrl, 'productId': productId, 'companyId': companyId, 'isParsed': False}
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
            total_pages = int(response.xpath('//span[contains(@class, "dots")]/following-sibling::a/text()').get())

            # looping into next page
            curr_page = re.findall('page/\d+', response.url)
            if curr_page:
                logger.debug('page %s' % curr_page)
                curr_page_req = int(re.findall('\d+', curr_page[0])[0])
            else:
                curr_page_req = 1
            next_page = curr_page_req + 1
            if next_page:
                next_page_url = response.url.split("page/")[0] + "page/" + str(next_page) + "/"
                yield scrapy.Request(response.urljoin(next_page_url), callback=self.parse)

        except Exception as exp:
            logger.error(exp)
        