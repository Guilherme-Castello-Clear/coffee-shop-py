from flask import Flask, render_template, request, redirect
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
import stripe

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///shop.db"

db = SQLAlchemy()
db.init_app(app)

stripe_keys = {
  'secret_key': 'sk_test_51OEdFdDA8J9AhIG9ho7a3LK8Cnk6o5TDs3mG1K8L60rwDvEvrDGpLaKPjSwtvu5WE7L4VrEOHdV6EsCTrQfQTIVG00fYwcgA5H',
  'publishable_key': 'pk_test_51OEdFdDA8J9AhIG9pDHiDoC0QrOrX5zwt8tnFs2JGpTMR3y8Rg1UbuT8uFYx3XaqGr3JmMA2ZzfkIQrz7YBdBydg00UVGof8yQ'
}
stripe.api_key = stripe_keys['secret_key']


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


@app.route('/remove_from_cart/<int:cart_item_id>')
def remove_from_cart(cart_item_id):
    to_delete = db.get_or_404(Cart, cart_item_id)
    db.session.delete(to_delete)
    db.session.commit()
    return redirect('/cart')


@app.route('/cart')
def cart():
    cart = Cart.query.all()
    products = []
    total_price = 0
    for item in cart:
        item_json = item.to_dict()
        item_product = db.get_or_404(Product, item_json['product_id'])
        total_price += item_product.price
        products.append(item_product)
    total_price *= 100
    return render_template('cart.html', products=products, key=stripe_keys['publishable_key'], total=total_price)


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
    return render_template('add.html')


@app.route('/checkout', methods=['POST'])
def checkout():
    cart = Cart.query.all()
    total_price = 0
    for item in cart:
        item_json = item.to_dict()
        item_product = db.get_or_404(Product, item_json['product_id'])
        total_price += int(item_product.price * 100)

    customer = stripe.Customer.create(
        email='sample@customer.com',
        source=request.form['stripeToken']
    )
    stripe.Charge.create(
        customer=customer.id,
        amount=total_price,
        currency='brl',
        description='Cafe'
    )

    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
