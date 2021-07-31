# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import Database

class RevitPipeline:

    def __init__(self):
        self.session, self.engine = Database.initSession()

    def process_item(self, item, spider):
        session = self.session()
        product = Database.Products()

        try:
            session.add(product)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        return item
