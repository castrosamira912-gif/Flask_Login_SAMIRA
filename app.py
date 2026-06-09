from flask import Flask, render_template
from flask import request, redirect, url_for

from models import db, User

from flask_bcrypt import Bcrypt

from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)

app = Flask(__name__)

app.config["SECRET_KEY"] = "123456"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

db.init_app(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        hash_password = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

        user = User(
            username=username,
            password=hash_password
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(
            username=username
        ).first()

        if user and bcrypt.check_password_hash(
                user.password,
                password):

            login_user(user)

            return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():

    return render_template(
        "dashboard.html",
        username=current_user.username
    )


@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("login"))


if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)