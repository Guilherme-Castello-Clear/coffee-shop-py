from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///shop.db"

db = SQLAlchemy()
db.init_app(app)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), unique=True, nullable=False)
    price = db.Column(db.Float, unique=True, nullable=False)
    description = db.Column(db.String(255), unique=True, nullable=False)
    current_cart = relationship("Cart", back_populates="product")


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = relationship("Product", back_populates="current_cart")

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
        }


with app.app_context():
    db.create_all()


@app.route('/cart')
def cart():
    cart = Cart.query.all()
    products = []
    for item in cart:
        item_json = item.to_dict()
        item_product = db.get_or_404(Product, item_json['product_id'])
        products.append(item_product)

    return render_template('cart.html', products=products)


@app.route('/add_to_cart/<int:id>', methods=["GET"])
def add_to_cart(id):
    add_product = db.get_or_404(Product, id)
    new_cart = Cart(
        product=add_product
    )
    db.session.add(new_cart)
    db.session.commit()
    return redirect('/')


@app.route('/', methods=['GET'])
def home():
    products = Product.query.all()
    return render_template('index.html', products=products)


@app.route('/product/<int:id>', methods=['GET'])
def product(id):
    current_product = db.get_or_404(Product, id)
    return render_template('product.html', product=current_product)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        new_product = Product(
            name=request.form.get('prod_name'),
            description=request.form.get('prod_desc'),
            price=request.form.get('prod_price'),
            image_url=request.form.get('prod_image')
        )
        db.session.add(new_product)
        db.session.commit()
        print('ok')
    return render_template('add.html')


if __name__ == "__main__":
    app.run(debug=True)
