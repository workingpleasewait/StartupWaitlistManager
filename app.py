import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from models import db, Subscriber

class Base(DeclarativeBase):
    pass

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
db.init_app(app)

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

    new_subscriber = Subscriber(full_name=full_name, email=email)
    db.session.add(new_subscriber)
    
    try:
        db.session.commit()
        return jsonify({"message": "Successfully subscribed!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred. Please try again."}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000)
