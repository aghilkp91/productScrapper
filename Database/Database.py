from sqlalchemy import Column, String, Integer, Boolean, create_engine, ForeignKey, DateTime, Numeric, func, Text, Float
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from Database import DBConfig
# import DBConfig
from sqlalchemy.exc import ProgrammingError, DatabaseError, SQLAlchemyError
from datetime import datetime
import csv
import os
import chardet
# import pandas as pd
from string import Template

Base = declarative_base()


def checkDatabase(inconn=DBConfig.DatabaseConfig.sqlalchemy_address):
    """
        This function is used to check the database if is accessible and it contains all the tables.

        We initialize the variables defined in the DBConfid.py file and connect to MSSQL DB.
        Then query all tables. If everything is successful, we return a true else throws the error

        :param inconn:Connection string to connect to DB
        :type inp_categories: str

        :return: Tuple with true if successsful or false with errors otherwise.
        :rtype: tuple 
    """
    try:
        user = DBConfig.DatabaseConfig.user
        password = DBConfig.DatabaseConfig.password
        database = DBConfig.DatabaseConfig.db
        server = DBConfig.DatabaseConfig.server
        # conn = Template(inconn).substitute(user=user, password=password, db=db)
        # conn = 'mssql+pyodbc://' + user + ':' + password + '@' + server + '/' + database + '?trusted_connection=yes&driver=SQL+Server'
        if DBConfig.DatabaseConfig.Auth_type == 'Windows':
            conn = 'mssql+pyodbc://@' + server + '/' + database + '?trusted_connection=yes&driver=SQL+Server'
        else:
            conn = 'mssql+pyodbc://' + user + ':' + password + '@' + server + '/' + database + '?trusted_connection=no&driver=SQL+Server'
        print(conn)
        engine = create_engine(conn, echo=True)
        db_session = sessionmaker(bind=engine)
        dbs = db_session()
        dbs.query(CompanyUrls).first()
        dbs.query(CategoryUrls).first()
        dbs.query(Products).first()
        dbs.query(ProductReviews).first()
        return (True,0,"")
    except ProgrammingError as err:
        return (False,err.code,err.orig)
    except DatabaseError as err:
        return (False, err.code, err.orig)

def  initSession(inconn=DBConfig.DatabaseConfig.sqlalchemy_address):
    """
        This function is used to initialze the DB session.

        We first try to initialize a database session using the credentials in the DBConfig.py
        Then we create an engine and db session which will be used for perfomring DB queries

        :param inconn:Connection string to connect to DB
        :type inp_categories: str

        :return: db_session Session variable created using the sessionmaker.
        :rtype: str

        :return: engine Engine created using the create_engine funuctin of sqlalchemy
        rtype: str 
    """
    # init connection
    user = DBConfig.DatabaseConfig.user
    password = DBConfig.DatabaseConfig.password
    database = DBConfig.DatabaseConfig.db
    server = DBConfig.DatabaseConfig.server
    # conn = Template(inconn).substitute(user=user, password=password, db=db)
    if DBConfig.DatabaseConfig.Auth_type == 'Windows':
        conn = 'mssql+pyodbc://@' + server + '/' + database + '?trusted_connection=yes&driver=SQL+Server'
    else:
        conn = 'mssql+pyodbc://' + user + ':' + password + '@' + server + '/' + database + '?trusted_connection=no&driver=SQL+Server'
    engine = create_engine(conn, pool_size=DBConfig.DatabaseConfig.mysql_max_connection)
    # create sessionmaker:
    #db_session = sessionmaker(bind=engine)
    db_session = sessionmaker(bind=engine,autoflush=False, expire_on_commit=False)

    return db_session, engine


def createTables(inconn=DBConfig.DatabaseConfig.sqlalchemy_address):
    """
        This function is used to create all the tables mentioned in Database.py file.

        This will first initialize the DB session and then create all tables as mentioned in engine

        :param inconn:Connection string to connect to DB
        :type inp_categories: str

        :return: True if it is successful, false and error code in case of error.
        :rtype: tuple
    """
    try:
        session, engine = initSession()
        Base.metadata.create_all(engine)
    except ProgrammingError as err:
        return (False,err.code,err.orig)
    except DatabaseError as err:
        return (False, err.code, err.orig)
    try:
        # insertCompanyUrls(session, engine, db)
        return (True, 0, "")
    except ProgrammingError as err:
        return (False, err.code, err.orig)
    except DatabaseError as err:
        return (False, err.code, err.orig)

class CompanyUrls(Base):
    """
        This Class mentions the table structure for Company Urls.

        id -> (Primary Key) Integer - Unique key to identify the company details
        name -> String - Name of the Company
        mainUrl -> String - Comapny Web URL
    """
    # Table name:
    __tablename__ = 'CompanyUrls'

    # Table structure:
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(64))
    mainUrl = Column(String(64))
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# def insertCompanyUrls(Session, engine, db):
#     try:
#         filename = os.path.dirname(os.path.abspath(__file__)) + '/companies.csv'
#         with open(filename, 'rb') as f:
#             result = chardet.detect(f.read())
#             df = pd.read_csv(filename, encoding=result['encoding'])
#             print(df['name'])
#             df.to_sql('CompanyUrls', con=engine, index=False, if_exists="append", schema='{0}.dbo'.format(db), method='multi')
#             print(engine.execute("SELECT * FROM CompanyUrls").fetchall())

#         # sheet = csv.(file_name=filename, delimiter=",")
#         # print(sheet)
#         # sheet.save_to_database(session=Session, table=CompanyUrls)
#     except DatabaseError as err:
#         err.orig = "Error while updating the database"
#         return err
#     except SQLAlchemyError as e:
#         error = str(e.__dict__['orig'])
#         return error

class CategoryUrls(Base):
    """
        This Class mentions the table structure for Category Urls.

        urlId -> (Primary Key) Integer - Unique key to identify the Category URL
        url -> String - Web URL for the Category Page of the products
        companyId -> (Foreign Key) String - Comapny id of the identify the company to which this url is associated
    """
    # Table name:
    __tablename__ = 'CategoryUrls'

    # Table structure:
    urlId = Column(String(64), index=True, primary_key=True)
    url = Column(String(64), index=False)
    companyId = Column(Integer, ForeignKey("CompanyUrls.id"), nullable=False)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Products(Base):
    """
        This Class mentions the table structure for Products.

        productId => (Primary Key) String - Product Id created using hash of the product url
        productUrl => String - Product Url where we crawl product information
        companyId => (ForeignKey : "CompanyUrls.id") Integer - Comapny id of the identify the company to which this url is associated
        originalCompanyName => String - Original Company name who manufactures the product
        itemNumber => String - Item number of product as mentioned in website
        itemName => String - Full Name of the product
        price => String - Price at which item is sold
        originalPrice => String - Original Price before discount if any
        discountPercent => String - Discounted percentage
        productRating => String - Product Rating of the product
        itemCategory => String - Category to which this prodcut belongs to
        itemStyle => String - Style to which the product belongs to
        color => String - Colors availble for the product
        size => String - Size available for the product
        gender => String - Gender to which product belongs to
        image => String - Unique Image url stored in our storage
        imageOriginalUrl => String - Original Image url mentioned in the website
        isParsed => Integer, default=0 - Flag to check if a particular product is already scrapped
    """
    # Table name:
    __tablename__ = 'Products'

    # Table structure:
    productId = Column(String(64), primary_key=True)
    productUrl = Column(String(255), index=True, nullable=False)
    companyId = Column(Integer, ForeignKey("CompanyUrls.id"), nullable=False)
    originalCompanyName = Column(String(64))
    itemNumber = Column(String(64))
    itemName = Column(String(128))
    price = Column(String(10))
    originalPrice = Column(String(10))
    discountPercent = Column(String(5))
    productRating = Column(String(5))
    itemCategory = Column(String(128))
    itemStyle = Column(String(128))
    color = Column(String(255))
    size = Column(String(255))
    gender = Column(String(6))
    image = Column(String(255))
    imageOriginalUrl = Column(String(255))
    isParsed = Column(Integer, unique=False, default=0)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ProductReviews(Base):
    """
    This Class mentions the table structure for Product Reviews.
    
    reviewId => (Primary key) String : Review Id to uniquely identify the review
    productId => (ForeignKey: "Products.productId") String
    companyId => (ForeignKey: "CompanyUrls.id") Integer
    reviewCreatedDate => DateTime - Review Created Date
    productPurchaseDate => DateTime - Product purchased date
    rating => Float - Rating as per the website
    ratingUpVotes => Integer - Count of upvotes for the rating
    ratingDownVotes => Integer - Count of Downvotes for the system
    text => Text - Review text containing the detailed reviews
    title => String - Review Title
    userId => String - User Id of the reviewer
    userName => String - Username of the reviewer
    bangForTheBuckRating => Integer - Bang for the buck by the user
    protectionDurabilityRating => Integer - protection and durability rating by the user
    featuresRating => Integer - Feature rating by the user
    comfortRating => Integer - Comfort rating by the user
    styleRating => Integer - Style rating by the user
    fitRating => Integer - Fit rating by the user
    airFlowRating => Integer - Air flow rating by the user
    """
     # Table name:
    __tablename__ = 'ProductReviews'

    # Table structure:
    reviewId = Column(String(64), primary_key=True)
    productId = Column(String(64), ForeignKey("Products.productId"), nullable=False)
    companyId = Column(Integer, ForeignKey("CompanyUrls.id"), nullable=False)
    reviewCreatedDate = Column(DateTime(timezone=True))
    productPurchaseDate = Column(DateTime(timezone=True))
    rating = Column(Float)
    ratingUpVotes = Column(Integer)
    ratingDownVotes = Column(Integer)
    text = Column(Text)
    title = Column(String(128))
    userId = Column(String(16))
    userName = Column(String(64))
    bangForTheBuckRating = Column(Integer)
    protectionDurabilityRating = Column(Integer)
    featuresRating = Column(Integer)
    comfortRating = Column(Integer)
    styleRating = Column(Integer)
    fitRating = Column(Integer)
    airFlowRating = Column(Integer)

