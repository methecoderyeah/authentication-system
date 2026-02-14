from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user, login_manager
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'
# CREATE DATABASE


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)
app.config['SECRET_KEY'] = 'totally secret'
# CREATE TABLE IN DB


class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))


with app.app_context():
    db.create_all()


the_login_manager = LoginManager()
the_login_manager.init_app(app)
@the_login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/')
def home():
    if current_user.is_authenticated:
        return render_template("index.html")
    else:
        return render_template("index.html")

@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        existing_user = User.query.filter_by(email=request.form.get('email')).first()
        if existing_user:
            flash("Email already exists. Try logging in?")
            return redirect(url_for("login"))
        else:
            name = request.form.get('name')
            user = User(
                name=name,
                email=request.form.get('email'),
                password=generate_password_hash(request.form.get('password'), method='scrypt', salt_length=8))
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('secrets', name=name))
    return render_template("register.html")

@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        try:
            user = User.query.filter_by(email=request.form.get('email')).first()
            if check_password_hash(pwhash=user.password, password=request.form.get('password')):
                login_user(user)
                return redirect(url_for('secrets', name=user.name))
            else:
                flash('Oops! Incorrect password.')
        except AttributeError:
            flash("Oops! That Email wasn't found in our database.")
    return render_template("login.html")

@app.route('/secrets')
@login_required
def secrets():
    name = request.args.get('name')
    return render_template("secrets.html", name = name)

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

@app.route('/download')
def download():
    return send_from_directory('static/files', 'cheat_sheet.pdf', as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
