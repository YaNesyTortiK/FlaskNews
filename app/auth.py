from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login/')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    data = db.is_user(email)
    if data:
        if db.check_password(email, password):
            name = data[3]
            session['is-logged'] = True
            session['name'] = name
            session['email'] = email
            return redirect('/')
        else:
            flash('Неправильно введен логин или пароль!')
            return redirect(url_for('auth.login'))
    else:
        flash(f'Такого пользователя не существует!')
        return redirect(url_for('auth.signup'))


@auth.route('/signup/')
def signup():
    return render_template('signup.html')

@auth.route('/signup/', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = db.is_user(email)

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Пользователь уже существует!')
        return redirect(url_for('auth.signup'))
    try:
        db.add_user(email=email, name=name, password=password)
    except FileExistsError:
        flash('Пользователь c таким именем уже существует, попробуйте другое!')
        return redirect(url_for('auth.signup'))

    # add the new user to the database
    session['is-logged'] = True
    session['name'] = name
    session['email'] = email

    return redirect('/')

@auth.route('/logout/')
def logout():
    session['is-logged'] = False
    try:
        print(session.pop('name'))
        print(session.pop('email'))
    except KeyError:
        pass
    return redirect('/')