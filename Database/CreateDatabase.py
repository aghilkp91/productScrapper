import Database
import sys


if __name__ == "__main__":
    status, code, msg = Database.checkDatabase()
    if status:
        print("Connected to Database ")
        sys.exit()
    if code != "f405":
        print("Connect to database failed: %s" % msg)
        sys.exit()
    resStatus, resCode, resMsg = Database.createTables()
    if resStatus:
        print("Connected to Database; Tables Created ")
    else:
        print("Creation of database/table failed: %s" % resMsg)
