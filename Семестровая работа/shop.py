from flask import Flask, render_template, request, redirect, flash, get_flashed_messages
from database import Database, User
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from functools import reduce

app = Flask(__name__)
app.secret_key = '999'

login = LoginManager(app)

db = Database()


@login.user_loader
def load_user(id):
    res = db.get(f"select login, password from user_account where user_id = {int(id)}")[0]
    user_login, user_password = res
    return User(db, user_login, user_password)


@app.route('/')
def render_shop():
    context = {
        'products': db.get("select * from product"),
        'categories': db.get("select * from category"),
        'user': current_user if current_user.is_authenticated else None,
    }
    if context['user']:
        context['favorite_products_ids'] = current_user.get_favorites()
        context['cart_products_ids'] = current_user.get_cart()
    return render_template('shop.html', **context)


@app.route('/products/<int:product_id>')
def render_product_page(product_id):
    product = db.get(f"select * from product where product_id = {product_id}")[0]
    category_id = product[1]
    category = db.get(f"select * from category where category_id = {category_id}")[0]
    context = {
        'product': product,
        'category': category,
        'categories': db.get("select * from category"),
        'user': current_user if current_user.is_authenticated else None,
    }
    if context['user']:
        context['favorite_products_ids'] = current_user.get_favorites()
        context['cart_products_ids'] = current_user.get_cart()
    return render_template('product.html', **context)


@app.route('/categories/<int:category_id>')
def render_category(category_id):
    context = {
        'products': db.get(f"select * from product where category_id = {category_id}"),
        'category_name': db.get(f"select name from category where category_id = {category_id}")[0][0],
        'categories': db.get("select * from category"),
        'user': current_user if current_user.is_authenticated else None,
    }
    if context['user']:
        context['favorite_products_ids'] = current_user.get_favorites()
        context['cart_products_ids'] = current_user.get_cart()
    return render_template('category.html', **context)


@app.route('/auth', methods=['POST'])
def auth():
    user_login = request.form['login']
    user_password = request.form['password']
    if request.form['action'] == 'login':
        if db.get(f"select * from user_account where login = '{user_login}' and password = '{user_password}'"):
            login_user(User(db, user_login, user_password))
        else:
            flash("Неправильный логин или пароль")
    else:
        if db.get(f"select * from user_account where login = '{user_login}'"):
            flash("Такой пользователь уже есть")
        else:
            db.post(
                f"insert into user_account(login, password, balance, is_admin, user_name, user_surname) values ('{user_login}', '{user_password}', 0, FALSE, '', '')")
            login_user(User(db, user_login, user_password))
    return redirect('/')


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/favorites')
def render_favorites():
    context = {
        'categories': db.get("select * from category"),
        'user': current_user if current_user.is_authenticated else None,
    }
    if context['user']:
        user_id = int(current_user.get_id())
        context['products'] = db.get(f"select * from (select product_id from favorites_product where user_id = {user_id}) as t1 natural join product")
        context['cart_products_ids'] = current_user.get_cart()
    return render_template('favorites.html', **context)


@app.route('/change-favorites', methods=['POST'])
@login_required
def change_favorites():
    user_id = int(current_user.get_id())
    product_id = int(request.form['id'])
    if db.get(f"select * from favorites_product where user_id = {user_id} and product_id = {product_id}"):
        db.post(f"delete from favorites_product where user_id = {user_id} and product_id = {product_id}")
    else:
        db.post(f"insert into favorites_product(user_id, product_id) VALUES ({user_id}, {product_id})")


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def render_profile():
    context = {
        'user': current_user if current_user.is_authenticated else None,
        'categories': db.get("select * from category")
    }
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        user_id = int(current_user.get_id())
        print(name, surname, user_id)
        db.post(f"update user_account set user_name = '{name}', user_surname = '{surname}' where user_id = {user_id}")
        return redirect('/profile')
    return render_template('profile.html', **context)


@app.route('/append-balance', methods=['POST'])
@login_required
def append_balance():
    user_id = int(current_user.get_id())
    current_balance = current_user.get_balance()
    db.post(f"update user_account set balance = {current_balance + 1500} where user_id = {user_id}")
    return redirect('/profile')


@app.route('/cart')
def render_cart():
    context = {
        'user': current_user if current_user.is_authenticated else None,
        'categories': db.get("select * from category")
    }
    if context['user']:
        user_id = int(current_user.get_id())
        context['products'] = db.get(f"select * from (select product_id, product_count from cart_item where user_id = {user_id}) as cart natural join product order by product_id")
        context['total_sum'] = reduce(lambda a, b: a + b[1] * b[5], context['products'], 0)
        context['total_products'] = reduce(lambda a, b: a + b[1], context['products'], 0)
        context['favorite_products_ids'] = current_user.get_favorites()
    return render_template('cart.html', **context)


@app.route('/append-cart', methods=['POST'])
@login_required
def append_cart():
    product_id = int(request.form['id'])
    user_id = int(current_user.get_id())
    if db.get(f"select * from cart_item where user_id = {user_id} and product_id = {product_id}"):
        count = db.get(f"select product_count from cart_item where user_id = {user_id} and product_id = {product_id}")[0][0]
        db.post(f"update cart_item set product_count = {count + 1} where user_id = {user_id} and product_id = {product_id}")
    else:
        db.post(f"insert into cart_item(user_id, product_id, product_count) VALUES ({user_id}, {product_id}, 1)")
    return redirect('/cart')


@app.route('/delete-from-cart', methods=['POST'])
@login_required
def delete_from_cart():
    product_id = int(request.form['id'])
    user_id = int(current_user.get_id())
    db.post(f"delete from cart_item where user_id = {user_id} and product_id = {product_id}")
    return redirect('/cart')


@app.route('/remove-from-cart', methods=['POST'])
@login_required
def remove_from_cart():
    product_id = int(request.form['id'])
    user_id = int(current_user.get_id())
    count = db.get(f"select product_count from cart_item where user_id = {user_id} and product_id = {product_id}")[0][0]
    if count < 2:
        db.post(f"delete from cart_item where user_id = {user_id} and product_id = {product_id}")
    else:
        db.post(f"update cart_item set product_count = {count - 1} where user_id = {user_id} and product_id = {product_id}")
    return redirect('/cart')


@app.route('/orders')
def render_orders():
    context = {
        'user': current_user if current_user.is_authenticated else None,
        'categories': db.get("select * from category")
    }
    if context['user']:
        user_id = int(current_user.get_id())
        orders_ids = list(map(lambda x: x[0], db.get(f"select order_id from user_order where user_id = {user_id}")))
        orders = [(i, db.get(f"select title, product_count from (select * from order_item where order_id = {i}) as t1 natural join product"), db.get(f"select sum(product_count * product.price) from (select * from order_item where order_id = {i}) as t1 natural join product")[0][0]) for i in orders_ids]
        context['orders'] = orders
    return render_template('orders.html', **context)


@app.route('/create-order', methods=['POST'])
@login_required
def create_order():
    user_id = int(current_user.get_id())
    products = db.get(f"select * from (select product_id, product_count from cart_item where user_id = {user_id}) as cart natural join product order by product_id")
    order_sum = reduce(lambda a, b: a + b[1] * b[5], products, 0)
    if current_user.get_balance() < order_sum:
        flash("Недостаточно средств")
        return redirect('/cart')
    db.post(f"update user_account set balance = {current_user.get_balance() - order_sum} where user_id = {user_id}")
    db.post(f"delete from cart_item where user_id = {user_id}")
    order_id = db.get(f"insert into user_order(user_id) values ({user_id}) returning order_id")[0][0]
    for product in products:
        db.post(f"insert into order_item(order_id, product_id, product_count) VALUES ({order_id}, {product[0]}, {product[1]})")
    flash("Заказ успешно создан")
    return redirect("/")


@app.route('/search')
def search_product():
    query = request.args.get('query').strip()
    context = {
        'products': db.get(f"select * from product where upper(title) ~ '{query.upper()}'"),
        'categories': db.get("select * from category"),
        'user': current_user if current_user.is_authenticated else None,
        'query': query
    }
    if context['user']:
        context['favorite_products_ids'] = current_user.get_favorites()
        context['cart_products_ids'] = current_user.get_cart()
    return render_template('search.html', **context)


@app.route('/new-product', methods=['GET', 'POST'])
@login_required
def add_new_product():
    if not current_user.is_admin():
        flash("Ты не админ, пашол нафиг!!")
        return redirect('/')
    if request.method == 'GET':
        context = {
            'categories': db.get("select * from category"),
            'user': current_user
        }
        return render_template('new-product.html', **context)
    else:
        category_id = request.form['category']
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        photo = request.files.get('photo')
        product_id = db.get(f"insert into product(category_id, title, description, price) VALUES ({category_id}, '{title}', '{description}', {price}) returning product_id")[0][0]
        photo.filename = f"{product_id}.{photo.filename.split('.')[1]}"
        photo.save(f'static/img/products/{photo.filename}')
        db.post(f"update product set photo_path = '{photo.filename}' where product_id = {product_id}")
        flash("Товар успешно добавлен")
        return redirect('/')


@app.route('/delete-product', methods=['POST'])
@login_required
def delete_product():
    product_id = request.form['id']
    db.post(f"delete from product where product_id = {product_id}")
    flash("Продукт успешно удален")
    return redirect('/')


@app.route('/change-product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def change_product(product_id):
    product_id = int(product_id)
    if not current_user.is_admin():
        flash("Ты не админ, пашол нафиг!!")
        return redirect('/')
    if request.method == 'GET':
        context = {
            'categories': db.get("select * from category"),
            'user': current_user,
            'product': db.get(f"select * from product where product_id = {product_id}")[0]
        }
        return render_template('change-product.html', **context)
    else:
        category_id = request.form['category']
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        photo = request.files.get('photo')
        photo.filename = f"{product_id}.{photo.filename.split('.')[1]}"
        photo.save(f'static/img/products/{photo.filename}')
        db.post(f"update product set category_id = {category_id}, title = '{title}', description = '{description}', price = '{price}', photo_path = '{photo.filename}' where product_id = {product_id}")
        flash("Товар успешно изменен")
        return redirect('/')


if __name__ == '__main__':
    app.run(port=8000, debug=True)
