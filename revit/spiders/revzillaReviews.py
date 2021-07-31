import scrapy
import Database.Database as Database
from scrapy import signals
import logging
import json
from string import Template
from datetime import datetime

logger = logging.getLogger(__name__)

class RevitReviewsSpider(scrapy.Spider):
    db, db_enigne = Database.initSession()
    company_id = None
    start_urls = []
    name = "revzillaReviews"
    COMPANY = "Revzilla"
    TOTAL_REVIEWS_PER_PAGE = 100
    url_to_parse = "https://cdn-ws.turnto.com/v5/sitedata/JlwvU6H5qZNF3NTsite/$itemNumber/d/review/en_US/$start_num/100/%7B%7D/RECENT/false"


    def start_requests(self):
        session = self.db()
        companyUrl = session.query(Database.CompanyUrls). \
            filter_by(name=self.COMPANY).first()
        companyUrl_id = companyUrl.id
        self.company_id = companyUrl_id

        # # To crawl only one product
        # result = session.query(Database.Products).filter(Database.Products.companyId == self.company_id).first()
        # itemNum = result.itemNumber.split("P")[-1]
        # meta = {'productId': result.productId, 'itemNumber': itemNum, 'start_num': 0}
        # review_url = Template(self.url_to_parse).substitute(itemNumber=itemNum, start_num=str(0))
        # yield scrapy.Request(review_url, dont_filter=True, meta=meta)


        # To crawl entire products
        result = session.query(Database.Products).filter(Database.Products.companyId == self.company_id).all()
        print('Total products %s' %(len(result)))
        for res in result:
            try:
                itemNum = res.itemNumber.split("P")[-1]
                meta = {'productId': res.productId, 'itemNumber': itemNum, 'start_num': 0}
                review_url = Template(self.url_to_parse).substitute(itemNumber=itemNum, start_num=0)
                yield scrapy.Request(review_url, dont_filter=True, meta=meta)
            except Exception as exp:
                logger.error("Failed to crawl product with id %s" %(res.productId))
                logger.error(exp)
            

    def parse(self, response):
        # Getting reviews and adding it to DB
        session = self.db()

        lists = []
        logger.info("Starting crawling of %s" % response.url)
        responses = json.loads(response.body)
        reviewids_results = session.query(Database.ProductReviews.reviewId).filter(Database.ProductReviews.productId == response.meta['productId']).all()
        review_ids = [ int(item[0]) for item in reviewids_results ]
        
        logger.info(review_ids)

        for resp in responses['reviews']:
            if int(resp['id']) in review_ids:
                continue
            try:
                dicts = { 
                    'productId': response.meta['productId'], 
                    'companyId': self.company_id, 
                    'reviewId': resp['id'],
                    'reviewCreatedDate': datetime.strptime(resp['dateCreatedFormatted'], '%b %d, %Y') if resp['dateCreatedFormatted'] else None,
                    'productPurchaseDate': datetime.strptime(resp['purchaseDateFormatted'], '%b %d, %Y') if resp['purchaseDateFormatted'] else None,
                    'rating': resp['rating'],
                    'ratingUpVotes': resp['upVotes'],
                    'ratingDownVotes': resp['downVotes'],
                    'text': resp['text'],
                    'title': resp['title'],
                    'userId': resp['user']['id'],
                    'userName': resp['user']['nickName']
                    }
                if resp['dimensions'] and len(resp['dimensions']) > 0:
                        dicts['bangForTheBuckRating'] = resp['dimensions'][0]['value']
                if resp['dimensions'] and len(resp['dimensions']) > 1:
                        dicts['protectionDurabilityRating'] = resp['dimensions'][1]['value'] 
                if resp['dimensions'] and len(resp['dimensions']) > 2:
                        dicts['featuresRating'] =  resp['dimensions'][2]['value'] 
                if resp['dimensions'] and len(resp['dimensions']) > 3:
                        dicts['comfortRating'] = resp['dimensions'][3]['value'] 
                if resp['dimensions'] and len(resp['dimensions']) > 4:
                        dicts['styleRating'] = resp['dimensions'][4]['value'] 
                if resp['dimensions'] and len(resp['dimensions']) > 5 :
                        dicts['fitRating'] = resp['dimensions'][5]['value'] 
                if resp['dimensions'] and len(resp['dimensions']) > 6:
                        dicts['airFlowRating'] = resp['dimensions'][6]['value'] 
                try:
                    dicts['title'] = (dicts['title'][:126] + '..') if len(dicts['title']) > 128 else dicts['title']
                except Exception as exp:
                    pass
                lists.append(dicts)
            except Exception as exp:
                logger.error(exp)
       
        if len(lists) > 0:
            try:
                session.bulk_insert_mappings(Database.ProductReviews, lists)
                session.commit()
            except Exception as exp:
                logger.error(exp)
            

        # Finding total products in page
        total_reviews = responses['total']

        # looping into next page
        try:
            curr_page = response.meta['start_num']
        except Exception as exp:
            raise exp
        
        next_page = curr_page + self.TOTAL_REVIEWS_PER_PAGE
        if total_reviews - next_page > 0:
            meta = response.meta
            meta['start_num'] = next_page
            next_page_url = Template(self.url_to_parse).substitute(itemNumber=response.meta['itemNumber'], start_num=str(next_page))
            yield scrapy.Request(response.urljoin(next_page_url), callback=self.parse, meta=meta)

