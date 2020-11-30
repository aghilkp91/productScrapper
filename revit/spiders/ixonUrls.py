import scrapy
import uuid
import re
import Database.Database as Database
from revit.spiders import revitUrlSpider
import logging

logger = logging.getLogger(__name__)

class IxonUrlSpider(revitUrlSpider.RevitUrlSpider):
    db, db_enigne = Database.initSession()
    company_id = None
    start_urls = ["https://www.ixon.com/en/products"]
    name = "ixonUrls"
    COMPANY = "Ixon"
    TOTAL_PRODUCTS_PER_PAGE = 12

    def __init__(self):
        super().__init__(self.COMPANY, self.name, self.TOTAL_PRODUCTS_PER_PAGE)

    def parse(self, response):
        # finding urls
        lists = []
        logger.info("Starting crawling of %s" % response.url)
        for url in response.xpath('//div[contains(@class,"mb-5")]/a/@href'):
            productUrl = url.get()
            productId = uuid.uuid3(uuid.NAMESPACE_URL, productUrl).hex
            companyId = self.company_id

            dicts = {'productUrl': productUrl, 'productId': productId, 'companyId': companyId, 'isParsed': False}
            lists.append(dicts)
        # print(dicts)
        # filename = 'revit/spiders/temp/-%s.txt' % page_name
        # with open(filename, 'a') as f:
        #     f.write(str(lists))
        session = self.db()
        session.bulk_update_mappings(Database.Products, lists)
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
