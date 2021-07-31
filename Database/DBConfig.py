class DatabaseConfig(object):
    """
        This Class mentions database config details for Database usage.

        sqlalchemy_address = "connection:string//$to$my$database"-> Connection string to be used for connecting to Database
        mysql_max_connection = 128 -> Maximum connection that will be made to the DB
        mysql_insert_number = 20000 -> Number of db queries done before resetting the connection
        user = 'Aghil Karadathodi Prasad' -> Username of connect to DB
        password = 'IWontGive' -> Password to connect to DB
        db = 'myDB' -> DB Name
        server = 'server' -> Server Name
    """  
    sqlalchemy_address = 'mysql+mysqlconnector://$user:$password@dashdb-txn-sbox-yp-lon02-13.services.eu-gb.bluemix.net:8443/$db'
    mysql_max_connection = 128
    mysql_insert_number = 20000
    user = 'aghil'
    password = 'aghil'
    db = 'dbname'
    server = 'servername'
    Auth_type = "user"

    def __init__(self):
        pass
        