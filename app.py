from flask_migrate import Migrate
from flask import Flask, render_template, request, jsonify, url_for, redirect
from flask_login import LoginManager, login_user, login_required, logout_user
import os
from models import db, Subscriber, User
from email_validator import validate_email, EmailNotValidError


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "your-secret-key")  # Add this line
db.init_app(app)
migrate = Migrate(app,db)

login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.json
    full_name = data.get('full_name')
    email = data.get('email')

    if not full_name or not email:
        return jsonify({"error": "Full name and email are required"}), 400

    if not is_valid_email(email):
        return jsonify({"error": "Invalid email address"}), 400

    existing_subscriber = Subscriber.query.filter_by(email=email).first()
    if existing_subscriber:
        return jsonify({"error": "Email already subscribed"}), 400

    new_subscriber = Subscriber(full_name=full_name, email=email)
    db.session.add(new_subscriber)

    try:
        db.session.commit()
        return jsonify({"message": "Successfully subscribed!"}), 201
    except Exception:
        db.session.rollback()
        return jsonify({"error": "An error occurred. Please try again."}), 500

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        return 'Invalid username or password', 401
    return render_template('admin_login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    subscribers = Subscriber.query.all()
    return render_template('admin_dashboard.html', subscribers=subscribers)

if __name__ == '__main__':
    with app.app_context():
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin')
            admin_user.set_password('password')
            db.session.add(admin_user)
            db.session.commit()
    app.run(host="0.0.0.0", port=5000)