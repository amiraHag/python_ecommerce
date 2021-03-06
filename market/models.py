from market import db, login_manager
from market import bcrypt
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer(), primary_key=True)
    user_name = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    budget = db.Column(db.Integer(), nullable=False, default=15000)
    user_items = db.relationship('Item', backref='owned_user', lazy=True)


    @property
    def formatted_budget(self):
        if len(str(self.budget)) >= 4:
            return f'{str(self.budget)[:-3]},{str(self.budget)[-3:]}$'
        else:
            return f'{self.budget}$'


    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, password_plain_text):
        self.password_hash = bcrypt.generate_password_hash(password_plain_text).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    def can_purchase(self, item_obj):
        return self.budget >= item_obj.price

    def can_sell(self, item_obj):
        return item_obj in self.user_items

    def get_id(self):
        try:
            return self.user_id
        except AttributeError:
            raise NotImplementedError('No `User id` attribute')


class Item(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False, unique=True)
    price = db.Column(db.Integer(), nullable=False)
    barcode = db.Column(db.String(length=12), nullable=False, unique=True)
    description = db.Column(db.String(length=1024), nullable=False, unique=True)
    owner = db.Column(db.Integer(), db.ForeignKey('user.user_id'))

    def __repr__(self):
        return f"Item {self.name}"

    def buy(self, user):
        self.owner = user.user_id
        user.budget -= self.price
        db.session.commit()

    def sell(self, user):
        self.owner = None
        user.budget += self.price
        db.session.commit()

# import os
# os.system('clear')

# from market.models import db

# To drop all info in the database
# db.drop_all()

# Create all tables in database
# db.create_all()

# import models
# from market.models import User,Item


# Create new user
# u1 = User(user_name="Amira", email_address="amira@theplaceholderworld.com", password_hash="123456")
# db.session.add(u1)
# db.session.commit()

# to see all users in the database
# User.query.all()

# to add item in the Item table
# i1 = Item(name="iphone 10", price = 800, barcode="1234567891", description = "description1")
# db.session.add(i1)
# db.session.commit()

# to see all items in the database
# Item.query.all()

# to filter items in the item table
# Item.query.filter_by(name="iphone 10") => get all items
# item1 = Item.query.filter_by(name="iphone 10").first() => get first item
# item1.owner = User.query.filter_by(user_name="Amira").first().user_id

# to rollback => db.session.rollback()

# item1 = Item.query.filter_by(name="iphone 10").first()
# item1.owner
# item1.owned_user