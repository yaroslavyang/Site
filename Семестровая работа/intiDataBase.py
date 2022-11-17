import psycopg2

con = psycopg2.connect(
    dbname="shop",
    user="postgres",
    password="M4X_$CvT",
    host="localhost",
    port=5432
)

cur = con.cursor()

cur.execute("CREATE TABLE if not exists category(category_id serial primary key, name varchar)")
cur.execute("CREATE TABLE if not exists product(product_id serial primary key, category_id integer references category(category_id), title varchar, description varchar, price integer, photo_path varchar)")
cur.execute("create table if not exists user_account(user_id serial primary key, login varchar, password varchar, balance integer, is_admin boolean, user_name varchar, user_surname varchar)")
cur.execute("create table if not exists favorites_product(user_id integer references user_account(user_id), product_id integer references product(product_id) on delete cascade)")
cur.execute("create table if not exists cart_item(user_id integer references user_account(user_id), product_id integer references product(product_id) on delete cascade, product_count integer)")
cur.execute("create table if not exists user_order(order_id serial primary key, user_id integer references user_account(user_id))")
cur.execute("create table if not exists order_item(order_id integer references user_order(order_id), product_id integer references product(product_id) on delete cascade, product_count integer)")

cur.execute("insert into category(name) values ('Техника')")
cur.execute("insert into category(name) values ('Продукты')")

cur.execute("insert into user_account(login, password, balance, is_admin) values ('admin', 'admin', 999999, TRUE)")

con.commit()

cur.close()
con.close()

