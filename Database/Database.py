from sqlalchemy import Column, String, Integer, Boolean, create_engine, ForeignKey, DateTime, Numeric, func
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import Database.DBConfig as DBConfig
# import DBConfig
from sqlalchemy.exc import ProgrammingError, DatabaseError, SQLAlchemyError
from datetime import datetime
import csv
import os
import chardet
import pandas as pd
from string import Template

Base = declarative_base()


def checkDatabase(inconn=DBConfig.DatabaseConfig.sqlalchemy_address):
    try:
        user = DBConfig.DatabaseConfig.user
        password = DBConfig.DatabaseConfig.password
        db = DBConfig.DatabaseConfig.db
        conn = Template(inconn).substitute(user=user, password=password, db=db)
        print(conn)
        engine = create_engine(conn, echo=True)
        db_session = sessionmaker(bind=engine)
        dbs = db_session()
        dbs.query(CompanyUrls).first()
        dbs.query(CategoryUrls).first()
        dbs.query(Products).first()
        return (True,0,"")
    except ProgrammingError as err:
        return (False,err.code,err.orig)
    except DatabaseError as err:
        return (False, err.code, err.orig)

def  initSession(inconn=DBConfig.DatabaseConfig.sqlalchemy_address):
    # init connection
    user = DBConfig.DatabaseConfig.user
    password = DBConfig.DatabaseConfig.password
    db = DBConfig.DatabaseConfig.db
    conn = Template(inconn).substitute(user=user, password=password, db=db)
    engine = create_engine(conn, pool_size=DBConfig.DatabaseConfig.mysql_max_connection)
    # create sessionmaker:
    #db_session = sessionmaker(bind=engine)
    db_session = sessionmaker(bind=engine,autoflush=False, expire_on_commit=False)

    return db_session, engine


def createTables(inconn=DBConfig.DatabaseConfig.sqlalchemy_address):
    try:
        db = DBConfig.DatabaseConfig.db
        session, engine = initSession()
        Base.metadata.create_all(engine)
    except ProgrammingError as err:
        return (False,err.code,err.orig)
    except DatabaseError as err:
        return (False, err.code, err.orig)
    try:
        insertCompanyUrls(session, engine, db)
        return (True, 0, "")
    except ProgrammingError as err:
        return (False, err.code, err.orig)
    except DatabaseError as err:
        return (False, err.code, err.orig)

class CompanyUrls(Base):
    # Table name:
    __tablename__ = 'CompanyUrls'

    # Table structure:
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(64))
    mainUrl = Column(String(64))
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

def insertCompanyUrls(Session, engine, db):
    try:
        filename = os.path.dirname(os.path.abspath(__file__)) + '/companies.csv'
        with open(filename, 'rb') as f:
            result = chardet.detect(f.read())
            df = pd.read_csv(filename, encoding=result['encoding'])
            print(df['name'])
            df.to_sql('CompanyUrls', con=engine, index=False, if_exists="append", schema='{0}.dbo'.format(db), method='multi')
            print(engine.execute("SELECT * FROM CompanyUrls").fetchall())

        # sheet = csv.(file_name=filename, delimiter=",")
        # print(sheet)
        # sheet.save_to_database(session=Session, table=CompanyUrls)
    except DatabaseError as err:
        err.orig = "Error while updating the database"
        return err
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error

class CategoryUrls(Base):
    # Table name:
    __tablename__ = 'CategoryUrls'

    # Table structure:
    urlId = Column(String(64), index=True, primary_key=True)
    url = Column(String(64), index=False)
    companyId = Column(Integer, ForeignKey("CompanyUrls.id"), nullable=False)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Products(Base):
    # Table name:
    __tablename__ = 'Products'

    # Table structure:
    productId = Column(String(64), primary_key=True)
    productUrl = Column(String(255), index=True, nullable=False)
    companyId = Column(Integer, ForeignKey("CompanyUrls.id"), nullable=False)
    itemNumber = Column(String(64))
    itemName = Column(String(128))
    price = Column(String(10))
    itemCategory = Column(String(64))
    color = Column(String(128))
    size = Column(String(64))
    gender = Column(String(6))
    image = Column(String(255))
    isParsed = Column(Integer, unique=False, default=0)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
