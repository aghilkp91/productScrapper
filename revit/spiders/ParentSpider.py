import scrapy
import os
import Database.Database as Database
from scrapy.http import Request
from revit import imageUtils
import time


class RevitSpider(scrapy.Spider):
    """ This is the base class which needs to inherited in the child class we create for all product spiders

        This class overwrites start_requests() and parse() functions from the Scrapy.Spider class.

        This also have functions which needs to be overwritten for custom logic or post processing of data for each items

        The spiders runs for the company initialized in the init function. So make sure COMPANY is initialized in the child function. 
        This company name is used to get company id from the CompanyUrls Table which is used to start the crawling of data

        Also when we want to create a new crawler for the website, inherit this class and overwrite the below finction and fill the xpath
        according to the data from the webpage.

            def parse(self, response):

                self.xpath_dicts = {
                    'itemName': "//h1/text()",                                                               # xpath for Item Name
                    'itemCategory': '/html/head/script[6]/text()',                                           # xpath for Item Category
                    'itemNumber': '//div[contains(@class,"product-show-details-ids")]/span/text()',          # xpath for Item Number
                    'originalCompanyName': '//a[contains(@class,"product-show-details-name")]/text()',       # xpath for Original CompanyName
                    'image': '//div[contains(@class,"product-show-media-image")]/meta/@content',             # xpath for Item Image
                    'imageOriginalUrl': '//div[contains(@class,"product-show-media-image")]/meta/@content',  # xpath for Original Image from website
                    'originalPrice': "//div[contains(@class,'price-was-discount')]/div/span/text()",         # xpath for Original Price
                    'discountPercent': "//span[contains(@class,'price-discount-percentage')]/text()",        # xpath for Discounted percent
                    'productRating': "//div[contains(@class,'product-rating__stars')]/@data-rating"          # xpath for Product Rating
                    'price': "//div[contains(@class,'product-rating__stars')]/@data-rating",                 # xpath for final price 
                    'itemStyle': "//div[contains(@class,'product-rating__stars')]/@data-rating",             # xpath for item style
                    'color': "//div[contains(@class,'product-rating__stars')]/@data-rating",                 # xpath for color
                    'size': "//div[contains(@class,'product-rating__stars')]/@data-rating",                  # xpath for size
                    'gender': "//div[contains(@class,'product-rating__stars')]/@data-rating"                 # xpath for gender
                }

        super().parse(response)
    """
    db, db_enigne = Database.initSession()
    img_utils = imageUtils.ImageUtils()
    xpath_dicts = {}

    def __init__(self, company, name):
        self.company_id = None
        self.name = name
        self.COMPANY = company

    def start_requests(self):
        """
        This is an over written function of base spider class

        This function initializes db and then find the company id from CompanyUrls Table. This id is used to find all the product urls which are not crawled. 
        Then web crawler will run for all the product URLs.
        """
        session = self.db()
        companyUrl = session.query(Database.CompanyUrls). \
            filter_by(name=self.COMPANY).first()
        companyUrl_id = companyUrl.id
        self.company_id = companyUrl_id

        # # To crawl only one product
        # result = session.query(Database.Products).filter(Database.Products.companyId == self.company_id,
        #                                                  Database.Products.isParsed == False).first()
        # meta = {'productId': result.productId, 'result': result}
        # yield Request(result.productUrl, dont_filter=True, meta=meta)

        # To crawl entire products
        result = session.query(Database.Products).filter(Database.Products.companyId == self.company_id,
                                                         Database.Products.isParsed == False).all()
        count = 0
        for res in result:
            # self.start_urls.append(res.url)
            if count == 100:
                time.sleep(60)
                count = 0
            meta = {'productId': res.productId, 'result': res}
            yield Request(res.productUrl, dont_filter=True, meta=meta)
            count = count + 1

    def get_category(self, inp_categories):
        """
        This function is used to categorize the products into custom categories as per REV'IT standards.

        First we define the set of REV'IT categories. Then we see if the category from the website belongs to one of the custom category. 
        It is added to the custom cateogry if it matched or we used the website category.

        :param inp_categories: Input Category from the crawled website
        :type inp_categories: str

        :return: The category as per REV'IT standards.
        :rtype: str 
        """
        available_categories = ['suit', 'motorcycle jackets', 'pant', 'motorcycle gloves', 'footware', 'protection', 'accessories', 'denim',
                                'heated', 'shoe', 'luggage', 'bag', 'blousons', 'parka', 'backpacks']
        if not inp_categories:
            return None
        in_categories = inp_categories.lower()
        result = []
        isPresent = False
        for substring in available_categories:
            if in_categories in substring:
                isPresent = True
                if substring == 'shoe':
                    result = 'footware'
                elif substring == 'bag' or substring == 'luggage':
                    result = 'backpacks'
                elif substring == 'denim':
                    result = 'pant'
                elif substring == 'blousons' or substring == 'parka':
                    result = 'jacket'
                else:
                    result = substring
        if not isPresent:
            result = in_categories
        return result

    def get_styles(self, inp_style):
        """
        This function is used to categorize the products into custom styles as per REV'IT standards.

        First we define the set of REV'IT styles. Then we see if the style from the website belongs to one of the custom style. 
        It is added to the custom style if it matched or we used the website style.

        :param inp_categories: Input style from the crawled website
        :type inp_style: str

        :return: The style as per REV'IT standards.
        :rtype: str 
        """
        available_styles = ['adventure', 'heritage', 'racing', 'urban', 'road', 'tour', 'mx', 'mtb', 'vintage', 'retro']
        if not inp_style:
            return None
        in_style = inp_style.lower()
        result = []
        isPresent = False
        for substring in available_styles:
            if substring in in_style:
                isPresent = True
                if substring == 'heritage' or substring == 'retro':
                    result.append('vintage')
                else:
                    result.append(substring)
        if not isPresent:
            return None
        return ' || '.join(result)


    def get_image(self, response, image_url, id):
        """
        This function is used to download an image from websites and upload it with unique name to Google Drive.

        First we find the extension of the image, download it to local and then upload it to Google Drive.
        We used the Imageutils module to perform the downlaod and upload

        :param response: HTML response from the crawled website
        :type response: str

        :param image_url: Image_url extracted using xpath
        :type image_url: str

        :param id: unique id to store in Google Drive
        :type id: str

        :return: Uplaoded image url.
        :rtype: str 
        """
        image_name = id + '.' + image_url.split(".")[-1]
        downloaded_image = imageUtils.ImageUtils.downloadImage(self.img_utils, image_url, image_name)
        uploaded_image = imageUtils.ImageUtils.uploadImage(self.img_utils, downloaded_image, image_name)
        os.remove(downloaded_image)
        return uploaded_image

    #overwrite the following functions to make changes to the value after crawling
    def getOriginalCompanyName(self, originalCompanyName_after_strip, response):
        """
        This function need to be overwritten in the child class to do data manipulation for Original Company Name.

        :param originalCompanyName_after_strip: Original Company Name extracted using xpath
        :type originalCompanyName_after_strip: str

        :param response: HTML response from the crawled website
        :type response: str

        :return: originalCompanyName_after_strip
        :rtype: str 
        """
        return originalCompanyName_after_strip

    def getItemNumber(self, itemNumber_after_strip, response):
        """
        This function need to be overwritten in the child class to do data manipulation for Item Number.

        :param itemNumber_after_strip: Item Number extracted using xpath
        :type itemNumber_after_strip: str

        :param response: HTML response from the crawled website
        :type response: str

        :return: itemNumber_after_strip
        :rtype: str 
        """
        return itemNumber_after_strip

    def getItemName(self, itemName_after_strip, response):
        """
        This function need to be overwritten in the child class to do data manipulation for Item Name.

        :param itemName_after_strip: itemName extracted using xpath
        :type itemName_after_strip: str

        :param response: HTML response from the crawled website
        :type response: str

        :return: itemName_after_strip
        :rtype: str 
        """
        return itemName_after_strip

    def getPrice(self, price_after_strip, response):
        """
        This function need to be overwritten in the child class to do data manipulation for price.

        :param price_after_strip: price extracted using xpath
        :type price_after_strip: str

        :param response: HTML response from the crawled website
        :type response: str

        :return: price_after_strip
        :rtype: str 
        """
        return price_after_strip

    def getOriginalPrice(self, originalPrice_after_strip, response):
        """
        This function need to be overwritten in the child class to do data manipulation for Original Price.

        :param originalPrice_after_strip: Original Price extracted using xpath
        :type originalPrice_after_strip: str

        :param response: HTML response from the crawled website
        :type response: str

        :return: originalPrice_after_strip
        :rtype: str 
        """
        return originalPrice_after_strip

    def getDiscountPercent(self, discountPercent_after_strip, response):
        """
        This function need to be overwritten in the child class to do data manipulation for Discount Percent.

        :param discountPercent_after_strip: Discount Percent extracted using xpath
        :type discountPercent_after_strip: str

        :param response: HTML response from the crawled website
        :type response: str

        :return: discountPercent_after_strip
        :rtype: str 
        """
        return discountPercent_after_strip

    def getProductRating(self, productRating_after_strip, response):
        """
        This function need to be overwritten in the child class to do data manipulation for Product Rating.

        :param productRating_after_strip: Product Rating extracted using xpath
        :type productRating_after_strip: str

        :param response: HTML response from the crawled website
        :type response: str

        :return: productRating_after_strip
        :rtype: str 
        """
        return productRating_after_strip

    def getItemCategory(self, itemCategory_after_strip, response):
        """
        This function need to be overwritten in the child class to do data manipulation for Item Category.

        :param itemCategory_after_strip: Item Category extracted using xpath
        :type itemCategory_after_strip: str

        :param response: HTML response from the crawled website
        :type response: str

        :return: itemCategory_after_strip
        :rtype: str 
        """
        return itemCategory_after_strip

    def getItemStyle(self, itemStyle_after_strip, response):
        """
        This function need to be overwritten in the child class to do data manipulation for Item Style.

        :param itemStyle_after_strip: Item Style extracted using xpath
        :type itemStyle_after_strip: str

        :param response: HTML response from the crawled website
        :type response: str

        :return: itemStyle_after_strip
        :rtype: str 
        """
        return itemStyle_after_strip

    def getColor(self, color_after_strip, response):
        """
        This function need to be overwritten in the child class to do data manipulation for color.

        :param color_after_strip: color extracted using xpath
        :type color_after_strip: str

        :param response: HTML response from the crawled website
        :type response: str

        :return: color_after_strip
        :rtype: str 
        """
        return color_after_strip

    def getSize(self, size_after_strip, response):
        """
        This function need to be overwritten in the child class to do data manipulation for Size.

        :param size_after_strip: Size extracted using xpath
        :type size_after_strip: str

        :param response: HTML response from the crawled website
        :type response: str

        :return: size_after_strip
        :rtype: str 
        """
        return size_after_strip
    
    def getGender(self, gender_after_strip, response):
        """
        This function need to be overwritten in the child class to do data manipulation for Gender.

        :param gender_after_strip: Gender extracted using xpath
        :type gender_after_strip: str

        :param response: HTML response from the crawled website
        :type response: str

        :return: gender_after_strip
        :rtype: str 
        """
        return gender_after_strip
    
    def getImage(self, image_after_strip, response):
        """
        This function need to be overwritten in the child class to do data manipulation for image.

        :param image_after_strip: Image extracted using xpath
        :type image_after_strip: str

        :param response: HTML response from the crawled website
        :type response: str

        :return: image_after_strip
        :rtype: str 
        """
        return image_after_strip

    def getImageOriginalUrl(self, imageOriginalUrl_after_strip, response):
        """
        This function need to be overwritten in the child class to do data manipulation for Image Original Url.

        :param imageOriginalUrl_after_strip: Image Original Url extracted using xpath
        :type imageOriginalUrl_after_strip: str

        :param response: HTML response from the crawled website
        :type response: str

        :return: imageOriginalUrl_after_strip
        :rtype: str 
        """
        return imageOriginalUrl_after_strip


    def parse(self, response):
        """
        This function parse through each xpath mentioned in the child function and apply the data manupulation functions if
        defined and store the values into DB.

        This is an extended function from the spider. Here we mention the parsing logic to map the data from crawled page to database.

        :param response: HTML response from the crawled website
        :type response: str
        """
        session = self.db()

        #Going through all xpath lists and apply xpath on each element if available
        originalCompanyName_from_xpath = None
        if 'originalCompanyName' in self.xpath_dicts:
            originalCompanyName_from_xpath = response.xpath(self.xpath_dicts['originalCompanyName']).get()
        originalCompanyName_after_strip = originalCompanyName_from_xpath.strip() if originalCompanyName_from_xpath else None
        originalCompanyName = self.getOriginalCompanyName(originalCompanyName_after_strip, response)

        itemNumber_from_xpath = None
        if 'itemNumber' in self.xpath_dicts:
            itemNumber_from_xpath = response.xpath(self.xpath_dicts['itemNumber']).get()
        itemNumber_after_strip = itemNumber_from_xpath.strip() if itemNumber_from_xpath else None
        itemNumber = self.getItemNumber(itemNumber_after_strip, response)

        itemName_from_xpath = None
        if 'itemName' in self.xpath_dicts:
            itemName_from_xpath = response.xpath(self.xpath_dicts['itemName']).get()
        itemName_after_strip = itemName_from_xpath.strip() if itemName_from_xpath else None
        itemName = self.getItemName(itemName_after_strip, response)

        price_from_xpath = None
        if 'price' in self.xpath_dicts:
            price_from_xpath = response.xpath(self.xpath_dicts['price']).get()
        price_after_strip = price_from_xpath.strip() if price_from_xpath else None
        price = self.getPrice(price_after_strip, response)

        originalPrice_from_xpath = None
        if 'originalPrice' in self.xpath_dicts:
            originalPrice_from_xpath = response.xpath(self.xpath_dicts['originalPrice']).get()
        originalPrice_after_strip = originalPrice_from_xpath.strip() if originalPrice_from_xpath else None
        originalPrice = self.getOriginalPrice(originalPrice_after_strip, response)

        discountPercent_from_xpath = None
        if 'discountPercent' in self.xpath_dicts:
            discountPercent_from_xpath = response.xpath(self.xpath_dicts['discountPercent']).get()
        discountPercent_after_strip = discountPercent_from_xpath.strip() if discountPercent_from_xpath else None
        discountPercent = self.getDiscountPercent(discountPercent_after_strip, response)

        productRating_from_xpath = None
        if 'productRating' in self.xpath_dicts:
            productRating_from_xpath = response.xpath(self.xpath_dicts['productRating']).get()
        productRating_after_strip = productRating_from_xpath.strip() if productRating_from_xpath else None
        productRating = self.getProductRating(productRating_after_strip, response)

        itemCategory_from_xpath = None
        if 'itemCategory' in self.xpath_dicts:
            itemCategory_from_xpath = response.xpath(self.xpath_dicts['itemCategory']).get()
        itemCategory_after_strip = itemCategory_from_xpath.strip() if itemCategory_from_xpath else None
        itemCategory = self.getItemCategory(itemCategory_after_strip, response)

        itemStyle_from_xpath = None
        if 'itemStyle' in self.xpath_dicts:
            itemStyle_from_xpath = response.xpath(self.xpath_dicts['itemStyle']).get()
        itemStyle_after_strip = itemStyle_from_xpath.strip() if itemStyle_from_xpath else None
        itemStyle = self.getItemStyle(itemStyle_after_strip, response)

        color_from_xpath = None
        if 'color' in self.xpath_dicts:
            color_from_xpath = response.xpath(self.xpath_dicts['color']).get()
        color_after_strip = color_from_xpath.strip() if color_from_xpath else None
        color = self.getColor(color_after_strip, response)

        size_from_xpath = None
        if 'size' in self.xpath_dicts:
            size_from_xpath = response.xpath(self.xpath_dicts['size']).get()
        size_after_strip = size_from_xpath.strip() if size_from_xpath else None
        size = self.getSize(size_after_strip, response)

        gender_from_xpath = None
        if 'gender' in self.xpath_dicts:
            gender_from_xpath = response.xpath(self.xpath_dicts['gender']).get()
        gender_after_strip = gender_from_xpath.strip() if gender_from_xpath else None
        gender = self.getGender(gender_after_strip, response)

        image_from_xpath = None
        if 'image' in self.xpath_dicts:
            image_from_xpath = response.xpath(self.xpath_dicts['image']).get()
        image_after_strip = image_from_xpath.strip() if image_from_xpath else None
        image = self.getImage(image_after_strip, response)

        imageOriginalUrl_from_xpath = None
        if 'imageOriginalUrl' in self.xpath_dicts:
            imageOriginalUrl_from_xpath = response.xpath(self.xpath_dicts['imageOriginalUrl']).get()
        imageOriginalUrl_after_strip = imageOriginalUrl_from_xpath.strip() if imageOriginalUrl_from_xpath else None
        imageOriginalUrl = self.getImageOriginalUrl(imageOriginalUrl_after_strip, response)

        dicts = {
            'originalCompanyName': originalCompanyName,
            'itemNumber': itemNumber,
            'itemName': itemName,
            'price': price,
            'originalPrice': originalPrice,
            'discountPercent': discountPercent,
            'productRating': productRating,
            'itemCategory': itemCategory,
            'itemStyle': itemStyle,
            'color': color,
            'size': size,
            'gender': gender,
            'image': image,
            'imageOriginalUrl': imageOriginalUrl,
            'isParsed': True
        }

        #adding it to DB
        session.query(Database.Products).filter_by(productId=response.meta['productId']).update(dicts)
        session.commit()

    
