class DatabaseConfig(object):
    sqlalchemy_address = 'mysql+mysqlconnector://$user:$password@localhost:3306/$db'
    mysql_max_connection = 128
    mysql_insert_number = 20000
    user = 'root'
    password = 'pass'
    db = 'webScrapping'


    def __init__(self):
        pass

