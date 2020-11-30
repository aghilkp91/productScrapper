import scrapy
import re
import Database.Database as Database
from scrapy.http import Request

class AlphineStars(scrapy.Spider):
    db, db_enigne = Database.initSession()
    name = "alphineStars"
    COMPANY = "Alpinestars"

    start_urls = []

    def start_requests(self):
        session = self.db()
        companyUrl = session.query(Database.CompanyUrls). \
            filter_by(name=self.COMPANY).first()
        companyUrl_id = companyUrl.id
        self.company_id = companyUrl_id
        result = session.query(Database.Products).filter(Database.Products.companyId == self.company_id, Database.Products.isParsed == False).all()

        # To crawl only one product
        # result = session.query(Database.Products).filter(Database.Products.companyId == self.company_id,
                                                         # Database.Products.isParsed == False).first()
        # meta = {'productId': result.productId}
        # yield Request(result.productUrl, dont_filter=True, meta=meta)

        #To crawl entire products
        for res in result:
            # self.start_urls.append(res.url)
            meta = {'productId': res.productId}
            yield Request(res.productUrl, dont_filter=True)


    def parse(self, response):
        session = self.db()

        itemName = response.xpath('//h1[@class="product-title"]/text()').get().strip()
        itemNumber = response.xpath('//div[contains(@class,"product-upc")]/span/text()').get().strip()
        price = response.xpath('//span[@class="money"]/text()').get().strip()
        itemCategory = response.xpath('//*[@id="shopify-section-static-product"]/nav/a[2]/text()').get()
        color = '||'.join(map(lambda x:x.get().strip(), response.xpath('//*[contains(@id,"product_form")]/div[1]/fieldset[2]/div/div/label/input/@value')))
        size = '||'.join(map(lambda x:x.get().strip(), response.xpath('//*[contains(@id,"product_form")]/div[1]/fieldset[1]/div/div/label/input/@value')))
        gender = 'Women' if re.search('women', itemName.lower()) else 'Men'
        # image
        print(response.meta['productId'])
        dicts = {
            'itemName': itemName,
            'itemCategory': itemCategory,
            'itemNumber': itemNumber,
            'price': price,
            'color': color,
            'size': size,
            'gender': gender,
            'isParsed': True
        }

        session.query(Database.Products).filter_by(productId=response.meta['productId']).update(dicts)
        session.commit()

