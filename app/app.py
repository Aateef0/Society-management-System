from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Set up Flask app
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Replace with a secure key

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:1206@localhost/society_management'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(50))

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_name = db.Column(db.String(100))
    tenant_name = db.Column(db.String(100))
    lease_end = db.Column(db.String(100))

class Visitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    visitor_name = db.Column(db.String(100))
    visit_date = db.Column(db.String(100))
    tenant_visited = db.Column(db.String(100))

# Routes
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        session['username'] = user.username
        session['role'] = user.role
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))

    flash('Invalid credentials', 'danger')
    return redirect(url_for('home'))
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already taken', 'danger')
            return redirect(url_for('register'))

        # Hash the password before storing it using a supported method
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password, role='tenant')

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('User registered successfully!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            print(f"Error occurred: {e}")  # Print the error in the console
            flash('Registration failed. Please try again.', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('home'))

    properties = Property.query.all()
    visitors = Visitor.query.all()

    return render_template('dashboard.html', properties=properties, visitors=visitors)

@app.route('/add_property', methods=['POST'])
def add_property():
    property_name = request.form['property_name']
    tenant_name = request.form['tenant_name']
    lease_end = request.form['lease_end']

    new_property = Property(property_name=property_name, tenant_name=tenant_name, lease_end=lease_end)
    db.session.add(new_property)
    db.session.commit()

    flash('Property added successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/add_visitor', methods=['POST'])
def add_visitor():
    visitor_name = request.form['visitor_name']
    visit_date = request.form['visit_date']
    tenant_visited = request.form['tenant_visited']

    new_visitor = Visitor(visitor_name=visitor_name, visit_date=visit_date, tenant_visited=tenant_visited)
    db.session.add(new_visitor)
    db.session.commit()

    flash('Visitor logged successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
