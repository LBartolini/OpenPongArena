import mysql.connector
from werkzeug.security import check_password_hash

class Database():
    SALT: str = '0pENponG4r3na'

    def __init__(self, db_config: dict) -> None:
        self.database = mysql.connector.connect(
            host=db_config['Host'],
            user=db_config['User'],
            password=db_config['Pass'],
            database=db_config['DB']
        )

    def verify_user(self, username: str, password: str) -> tuple[bool, float]:
        # T=success, F=failure
        coded_password = self.SALT+username+password
        
        with self.database.cursor() as cursor:
            sql = "SELECT  Password, ELO FROM User WHERE Username=%s"
            cursor.execute(sql, (username,))
            res = cursor.fetchall()
            if len(res)!=1 or not check_password_hash(res[0][0], coded_password):
                return False, 0

            return True, float(res[0][1])

    def log_game(self, user1: str, user2: str, change1: float, change2: float) -> None:
        pass