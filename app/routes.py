from flask import render_template, url_for, flash, redirect, request
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, SettingsForm
from app.models import User, Settings
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
@app.route("/home")
def home():
    return render_template('index.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/dashboard")
@login_required
def dashboard():
    settings = Settings.query.filter_by(user_id=current_user.id).first()
    return render_template('dashboard.html', title='Dashboard', settings=settings)

@app.route("/settings", methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm()
    if form.validate_on_submit():
        settings = Settings.query.filter_by(user_id=current_user.id).first()
        if settings:
            settings.risk_percentage = form.risk_percentage.data
            settings.account_balance = form.account_balance.data
            settings.symbols = form.symbols.data
        else:
            settings = Settings(risk_percentage=form.risk_percentage.data, account_balance=form.account_balance.data, symbols=form.symbols.data, user_id=current_user.id)
            db.session.add(settings)
        db.session.commit()
        flash('Your settings have been updated!', 'success')
        return redirect(url_for('dashboard'))
    elif request.method == 'GET':
        settings = Settings.query.filter_by(user_id=current_user.id).first()
        if settings:
            form.risk_percentage.data = settings.risk_percentage
            form.account_balance.data = settings.account_balance
            form.symbols.data = settings.symbols
    return render_template('settings.html', title='Settings', form=form)
