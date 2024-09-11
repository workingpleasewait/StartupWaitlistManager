import os
import logging
import random
import string
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import inspect
from models import db, Subscriber
from email_validator import validate_email, EmailNotValidError

class Base(DeclarativeBase):
    pass

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
db.init_app(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Log database connection info (without sensitive data)
logger.info(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI'].split('@')[-1]}")

def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

def generate_referral_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.json
    full_name = data.get('full_name')
    email = data.get('email')
    referral_code = data.get('referral_code')

    if not full_name or not email:
        return jsonify({"error": "Full name and email are required"}), 400

    if not is_valid_email(email):
        return jsonify({"error": "Invalid email address"}), 400

    try:
        logger.info(f"Attempting to subscribe: {email}")
        existing_subscriber = Subscriber.query.filter_by(email=email).first()
        if existing_subscriber:
            logger.info(f"Email already subscribed: {email}")
            return jsonify({"error": "Email already subscribed"}), 400

        new_referral_code = generate_referral_code()
        new_subscriber = Subscriber(full_name=full_name, email=email, referral_code=new_referral_code)

        if referral_code:
            referrer = Subscriber.query.filter_by(referral_code=referral_code).first()
            if referrer:
                new_subscriber.referrer_id = referrer.id
                referrer.referral_count += 1
                logger.info(f"Referral successful: {email} referred by {referrer.email}")
            else:
                logger.warning(f"Invalid referral code used: {referral_code}")

        db.session.add(new_subscriber)
        db.session.commit()
        logger.info(f"New subscriber added: {email}")
        return jsonify({
            "message": "Successfully subscribed!",
            "referral_code": new_referral_code
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in subscribe: {str(e)}")
        return jsonify({"error": "An error occurred. Please try again."}), 500

@app.route('/referral_stats/<referral_code>')
def referral_stats(referral_code):
    try:
        subscriber = Subscriber.query.filter_by(referral_code=referral_code).first()
        if not subscriber:
            return jsonify({"error": "Invalid referral code"}), 404
        
        return jsonify({
            "referral_count": subscriber.referral_count,
            "referral_code": subscriber.referral_code
        })
    except Exception as e:
        logger.error(f"Error in referral_stats: {str(e)}")
        return jsonify({"error": "An error occurred. Please try again."}), 500

def check_database_schema():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    logger.info(f"Tables in the database: {tables}")
    if 'subscriber' in tables:
        columns = [col['name'] for col in inspector.get_columns('subscriber')]
        logger.info(f"Columns in the 'subscriber' table: {columns}")
    else:
        logger.error("'subscriber' table not found in the database")

def test_database_connection():
    try:
        with db.engine.connect() as connection:
            logger.info("Successfully connected to the database")
            return True
    except Exception as e:
        logger.error(f"Error connecting to the database: {str(e)}")
        return False

if __name__ == '__main__':
    with app.app_context():
        if test_database_connection():
            try:
                db.create_all()
                logger.info("Database tables created successfully")
            except Exception as e:
                logger.error(f"Error creating database tables: {str(e)}")
            check_database_schema()
        else:
            logger.error("Failed to connect to the database. Please check your database configuration.")
    app.run(host="0.0.0.0", port=5000, debug=True)
