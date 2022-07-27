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
        with self.database.cursor() as cursor:
            sql = "INSERT INTO GameLog (PlayerOne, PlayerTwo, ChangeOne, ChangeTwo) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (user1, user2, change1, change2))

            sql = "SELECT ELO FROM User WHERE ID=%s OR ID=%s"
            cursor.execute(sql, (user1, user2))
            res = cursor.fetchall()

            elo1, elo2 = res[0][0], res[1][0]
            
            sql = "UPDATE User SET ELO=%s WHERE ID=%s"
            cursor.execute(sql, (elo1+change1, user1))
            
            sql = "UPDATE User SET ELO=%s WHERE ID=%s"
            cursor.execute(sql, (elo2+change2, user2))

            self.database.commit()


if __name__ == '__main__':
    import utils

    env_config: dict = utils.open_environment()
    database = Database(env_config['DB'])
    database.log_game(1, 2, 10, -10)
            