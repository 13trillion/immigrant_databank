# @Author: Gutu, Bilal <Bilal_gutu>
# @Date:   2022-04-15T15:30:36-04:00
# @Last modified by:   Bilal_gutu
# @Last modified time: 2022-04-18T00:06:34-04:00
import functools

from flask import (
    Blueprint, Flask, flash, g, redirect, render_template, request, session, url_for, abort
)

from werkzeug.security import check_password_hash, generate_password_hash
from db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

conn = get_db()

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        gender = request.form['gender']
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        user_type = request.form['user_type']

        db = get_db()
        error = None

        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif not name:
            error = 'Name is required.'

        if error is None:
            try:
                statement = "INSERT INTO users (email, password, name, gender, address, city, state, user_type) VALUES (%s, %s, %s,%s, %s, %s, %s, %s)"
                params = email, generate_password_hash(password), name, gender, address, city, state, user_type
                db.execute(
                    statement,params,
                )
            except Exception as e:
                error = f"User {email} is already registered."
            if (user_type == 'agency'):
                cur = conn.execute('SELECT uid FROM users WHERE email = %s', (email))
                id = cur.fetchone()
                return redirect(url_for("auth.register_agency", uid = id))
            else:
                # return redirect(url_for("auth.register_immigrant", uid = id))
                return redirect(url_for("auth.login"))
            # else:
            #     return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/register_agency/<uid>', methods=('GET', 'POST'))
def register_agency(uid):

    # Allow user to sign up to a specific category
    cursor = conn.execute("SELECT * FROM Category")
    cate = {}
    for result in cursor:
        cate[result['category_id']] = {
            'category_name': result['category_name']
        }
    cursor.close()
    context = dict(category = cate)

    print(uid[2])
    # print(request.args['uid'])

    if request.method == 'POST':
        uid = uid[2],
        agency_type = request.form['agency_type']
        established = request.form['established']
        agency_size = request.form['agency_size']
        budget = request.form['budget']

        db = get_db()
        error = None
        print(uid[0])
        if not agency_type:
            error = 'Agency type is required.'
        elif not established:
            error = 'Date established is required.'
        elif not agency_size:
            error = 'Agency size is required.'
        elif not budget:
            error = 'Budget size is required.'

        if error is None:
            try:
                statement = "INSERT INTO agency (uid, agency_type, established, agency_size, budget) VALUES (%s, %s, %s, %s, %s)"
                params = uid[0], agency_type, established, agency_size, budget
                db.execute(
                    statement,params,
                )
            except Exception as e:
                error = f"Agency {uid[0]} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/agency.html', **context)

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None

        user = db.execute(
            'SELECT * FROM users WHERE email = %s', (email)
        ).fetchone()

        if user is None:
            error = 'Incorrect email.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['uid']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = conn.execute(
            'SELECT * FROM users WHERE UID = %s', (user_id)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
