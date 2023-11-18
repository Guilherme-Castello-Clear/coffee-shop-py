from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///shop.db"

db = SQLAlchemy()
db.init_app(app)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    price = db.Column(db.Float, unique=True, nullable=False)
    description = db.Column(db.String(255), unique=True, nullable=False)


with app.app_context():
    db.create_all()


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/product', methods=['GET'])
def product():
    return render_template('product.html')


if __name__ == "__main__":
    app.run(debug=True)
