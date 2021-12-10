import os
from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, HiddenField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import InputRequired

app = Flask(__name__)

photos = UploadSet('photos', IMAGES)

app.config['UPLOADED_PHOTOS_DEST'] = 'static/images'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trendy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
configure_uploads(app, photos)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    price = db.Column(db.Integer)  # in cents
    stock = db.Column(db.Integer)
    description = db.Column(db.String(500))
    image = db.Column(db.String(100))

class AddProduct(FlaskForm):
    name = StringField('Product Name', validators=[
        InputRequired('Name is required!')
    ])
    price = IntegerField('Product Price', validators=[
        InputRequired('Price is required!')
    ])
    stock = IntegerField('Openning Stock')
    description = TextAreaField('Description')
    image = FileField('Product Image', validators=[
        FileAllowed(IMAGES, 'Only images are accepted!'),
        InputRequired()
    ])

class AddToCart(FlaskForm):
    quantity = IntegerField('Quantity', validators=[InputRequired()])
    product_id = HiddenField('ID')

@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/product/<id>')
def product(id):
    product = Product.query.filter(Product.id==id).first()
    quantity = AddToCart()
    return render_template('view-product.html', product=product, quantity=quantity)

@app.route('/quick-add/<id>')
def quick_add(id):
    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append({'product_id' : id, 'quantity' : 1})
    session.modified = True

    return redirect(url_for('index'))

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    if 'cart' not in session:
        session['cart'] = []

    form = AddToCart()
    if form.validate_on_submit():
        session['cart'].append({'product_id' : form.product_id.data, 'quantity': form.quantity.data})
        session.modified = True

    return redirect(url_for('index'))

@app.route('/remove-from_cart/<index>')
def remove_from_cart(index):
    del session['cart'][int(index)]
    session.modified = True
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    products = []
    form = AddToCart()

    grand_total = 0
    index = 0
    for item in session['cart']:
        product = Product.query.filter(Product.id==item['product_id']).first()
        quantity = int(item['quantity'])
        total = product.price * quantity

        grand_total += total

        products.append({
            'id' : product.id,
            'index' : index,
            'name' : product.name,
            'price' : product.price,
            'image' : product.image,
            'quantity' : quantity,
            'total' : total
        })
        index += 1

    return render_template('cart.html', products=products, form=form, grand_total=grand_total)

@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

@app.route('/admin')
def admin():
    products = Product.query.all()
    products_in_stock = Product.query.filter(Product.stock > 0).count()

    return render_template('admin/index.html', admin=True, products=products, products_in_stock=products_in_stock)

@app.route('/admin/add', methods=['GET', 'POST'])
def add():
    form = AddProduct()
    
    if form.validate_on_submit():
        image_name = photos.save(form.image.data)
        new_product = Product(
            name = form.name.data, 
            price = form.price.data,
            stock = form.stock.data,
            description = form.description.data,
            image = image_name
        )

        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('add'))
    return render_template('admin/add-product.html', admin=True, form=form)

@app.route('/admin/order')
def order():
    return render_template('admin/view-order.html', admin=True)

if __name__ == '__main__':
    app.run(debug=True)