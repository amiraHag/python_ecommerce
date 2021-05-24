from market import app
from flask import render_template, redirect, url_for, flash, request
from market.models import Item, User
from market.forms import RegisterForm, LoginForm, PurchaseItemForm
from market import db
from flask_login import login_user, logout_user, login_required, current_user


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html', page_title='Home Page')


@app.route('/shop', methods=['GET', 'POST'])
@login_required
def shop_page():
    purchase_form = PurchaseItemForm()
    # if purchase_form.validate_on_submit():
        # print(purchase_form.__dict__)
        # print(purchase_form['submit'])
        # print(request.form.get('purchased_item'))
    if request.method == "POST":
        purchased_item = request.form.get('purchased_item')
        p_item_obj = Item.query.filter_by(name=purchased_item).first()
        if p_item_obj:
            if current_user.can_purchase(p_item_obj):
                p_item_obj.buy(current_user)
                flash(f"Congratulations! You purchased {p_item_obj.name} for {p_item_obj.price}$", category='success')
            else:
                flash(f"Unfortunately, you don't have enough money to purchase {p_item_obj.name}!", category='danger')
        return redirect(url_for('shop_page'))
    if request.method == "GET":
        items = Item.query.filter_by(owner=None)
        return render_template('shop.html', shop_items=items, page_title='Shop Page', purchase_form=purchase_form)


@app.route('/about')
def about_page():
    return render_template('about.html', page_title='About Page')


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(user_name=form.username.data,
                              email_address=form.email.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.user_name}", category='success')
        return redirect(url_for('shop_page'))
    if form.errors != {}:
        for err_message in form.errors.values():
            flash(f' There was an error in creating a User {err_message} ', category='danger')

    return render_template('register.html', form=form, page_title='Register Page')


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(user_name=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.user_name}', category='success')
            return redirect(url_for('shop_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')
    return render_template('login.html', form=form, page_title='Login Page')


@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for('home_page'))


@app.route('/about/<username>')
def about_page_specific_user(username):
    return render_template('about.html', page_title=f'{username.capitalize()} User Page')