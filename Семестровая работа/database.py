import psycopg2


class Database:
    def __init__(self):
        con = psycopg2.connect(
            dbname="shop",
            user="postgres",
            password="M4X_$CvT",
            host="localhost",
            port=5432
        )
        self.cur = con.cursor()
        con.autocommit = True

    def get(self, query):
        self.cur.execute(query)
        tmp = self.cur.fetchall()
        return tmp

    def post(self, query):
        self.cur.execute(query)


class User:
    def __init__(self, db: Database, login, password):
        self.db = db
        self.login = login
        self.password = password
        self.id = self.db.get(f"select user_id from user_account where login = '{self.login}'")[0][0]

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def get_balance(self):
        return self.db.get(f"select balance from user_account where login = '{self.login}'")[0][0]

    def get_name(self):
        return self.db.get(f"select user_name from user_account where login = '{self.login}'")[0][0]

    def get_surname(self):
        return self.db.get(f"select user_surname from user_account where login = '{self.login}'")[0][0]

    def get_favorites(self):
        return list(map(lambda x: x[0], self.db.get(f"select product_id from favorites_product where user_id = {self.id}")))

    def get_cart(self):
        return list(map(lambda x: x[0], self.db.get(f"select * from (select product_id from cart_item where user_id = {self.id}) as cart natural join product")))

    def is_admin(self):
        return self.db.get(f"select is_admin from user_account where user_id = {self.id}")[0][0]
