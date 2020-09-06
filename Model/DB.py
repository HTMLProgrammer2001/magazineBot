from mysql.connector import connect, Error
from json import loads, dumps

from Common import config


class DB:
    conn = None

    def __init__(self):
        try:
            # connect to db
            self.conn = connect(**config.dbConnection)
            self.cursor = self.conn.cursor(buffered=True)
        except Error as err:
            print('Error in connection', err.msg)
            exit(1)

        # create table for bot
        self.createTable()

    def getCur():
        self.close()

        self.conn = connect(**config.dbConnection)
        self.cursor = self.conn.cursor(buffered=True)

        return self.cursor

    def createTable(self):
        try:
            self.getCur().execute('''CREATE TABLE IF NOT EXISTS `bot`(
                `userID` INT UNIQUE NOT NULL,
                `state` INT NOT NULL,
                `filters` TEXT DEFAULT NULL,
                `page` INT DEFAULT 1
            )''')

            self.conn.commit()
        except Error as err:
            print('Error in creating table: ', err.msg)
            exit(1)

    def createUser(self, userID, state=1, filters=None):
        if filters is None:
            filters = dict()

        try:
            # change user only if he exists in db else create new user
            if self.hasUser(userID):
                self.changeUserState(userID, state=state, filters=filters)
            else:
                self.getCur().execute("INSERT INTO `bot` (`userID`, `state`, `filters`) "
                                    "VALUES (%s, %s, %s)", (userID, state, dumps(filters)))

                self.conn.commit()
        except Error as err:
            print('Error in user adding: ', err.msg)

    def changeUserState(self, userID, **fields):
        try:
            if self.hasUser(userID):
                query = "UPDATE `bot` SET `userID`=`userID`"

                for key, val in fields.items():
                    if isinstance(val, dict):
                        query += f", `{key}` = '{dumps(val)}'"
                    else:
                        query += f", `{key}` = {val}"

                query += f" WHERE `userID` = {userID}"

                self.getCur().execute(query)
                self.conn.commit()
            else:
                self.createUser(userID, fields.get('state', 1))
        except Error as err:
            print('Error in change user: ', err.msg)

    def deleteUser(self, userID):
        try:
            self.getCur().execute("DELETE FROM `bot` WHERE `userID` = %s", (userID,))
            self.conn.commit()
        except Error as err:
            print('Error in change user: ', err.msg)

    def hasUser(self, userID: str) -> bool:
        try:
            self.getCur().execute("SELECT * FROM `bot` WHERE `userID` = %s", (userID,))

            return self.cursor.rowcount > 0
        except Error as err:
            print('Error in check user: ', err.msg)

    def getUser(self, userID):
        try:
            self.getCur().execute("SELECT * FROM `bot` WHERE `userID` = %s", (userID,))

            row = self.cursor.fetchone()

            if not row:
                return False

            user = list(row)
            user[2] = loads(user[2])

            return user
        except Error as err:
            print('Error in get user: ', err.msg)

    def userHasState(self, userID: str, state: int) -> bool:
        user = self.getUser(userID)
        return user and user[1] == state

    def close(self):
        self.conn.close()
        self.cursor.close()


db = DB()
