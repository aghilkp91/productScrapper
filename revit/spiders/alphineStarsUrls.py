import scrapy
import uuid
import re
import Database.Database as Database
from revit.spiders import revitUrlSpider

from scrapy import signals


class AlphineStarsUrlSpider(revitUrlSpider.RevitUrlSpider):
    db, db_enigne = Database.initSession()
    company_id = None
    start_urls = []
    name = "alpineStarsUrls"
    COMPANY = "Alpinestars"
    TOTAL_PRODUCTS_PER_PAGE = 24

    def __init__(self):
        super().__init__(self.COMPANY, self.name, self.TOTAL_PRODUCTS_PER_PAGE)

    def parse(self, response):
        # finding urls
        page_name = response.url.split('/')[-1]
        lists = []
        print("Starting crawling of %s" % response.url)
        for url in response.xpath('//h2[@class="productitem--title"]/a/@href'):
            productUrl = response.url.split("?")[0] + url.get()
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
        total_products = 0
        for script in response.xpath("//script/text()"):
            # m = re.findall('collection_count', script.get())
            m = re.search('collection_count: (.+?),', script.get())

            if m:
                # m = re.search('collection_count: (.+?),', script.get())
                # print(m)
                total_products = int(re.findall(r'\d+', m.group(1))[0])
        print("Total products : %s" % str(total_products))

        # looping into next page
        page = re.findall('page=\d+', response.url)
        if page:
            print('page %s' % page)
            curr_page_req = int(re.findall('\d+', page[0])[0])
        else:
            curr_page_req = 1
        next_page = curr_page_req + 1 if (total_products / (self.TOTAL_PRODUCTS_PER_PAGE * curr_page_req)) >= 1 else 0
        if next_page:
            next_page_url = response.url.split("?page")[0] + "?page=" + str(next_page)
            yield scrapy.Request(response.urljoin(next_page_url), callback=self.parse)
