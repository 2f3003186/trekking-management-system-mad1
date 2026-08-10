from model import db, User
import os
from flask import Flask
from werkzeug.security import generate_password_hash, check_password_hash

cur_dir = os.path.dirname(__file__)

def create_app():
    app = Flask(__name__, template_folder="templates")

    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(os.path.abspath(cur_dir) , "database.sqlite3")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = "My-Secret-Key-123456"
    db.init_app(app)

    with app.app_context():
        db.create_all()
        create_admin()

    return app

def create_admin():
    admin_exists = User.query.filter_by(role="admin").first()

    if not admin_exists:
        admin = User(
            name = "admin",
            password = generate_password_hash("password"),
            role = "admin",
            email = "admin_123@gmail.com",
            ph_num = "1234567890"
        )
        db.session.add(admin)
        db.session.commit()

app = create_app()
from controllers.auth import *

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)

