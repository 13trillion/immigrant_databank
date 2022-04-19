# @Author: Gutu, Bilal <Bilal_gutu>
# @Date:   2022-04-15T15:30:36-04:00
# @Last modified by:   Bilal_gutu
# @Last modified time: 2022-04-18T23:02:46-04:00
import functools

from flask import (
    Blueprint, Flask, flash, g, redirect, render_template, request, session, url_for, abort
)

from werkzeug.security import check_password_hash, generate_password_hash
from db import get_db, close_db


bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = get_db()
  except:
    print ("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@bp.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    close_db(g.conn)
  except Exception as e:
    pass

@bp.route('/post', methods=('GET', 'POST'))
def post():
    cursor = g.conn.execute("SELECT * FROM Category")
    cate = {}
    for result in cursor:
      cate[result['category_id']] = {
          'category_name': result['category_name']
      }

    context = dict(categories = cate)
    cursor.close()

    if request.method == 'POST':
        user_id = session.get('user_id')
        category_id = request.form['category']
        post_title = request.form['post_title']
        post_description = request.form['post_description']

        mode = request.form['mode']
        accessibility = request.form['accessibility']
        url = request.form['url']

        params = (user_id, category_id, post_title, post_description)
        if user_id and category_id and post_title and post_description:
            try:
                cur = g.conn.execute("INSERT INTO Posts(uid, category_id, post_title, post_description) VALUES (%s, %s, %s, %s)", params)
            except Exception as e:
                error = f"Something went wrong"

            pid = g.conn.execute("SELECT pid FROM Posts GROUP BY pid ORDER BY pid DESC LIMIT 1;").fetchone()[0]
            resc_params = (pid, mode, accessibility, url)
            g.conn.execute("INSERT INTO Resource(pid, mode, accessibility, url) VALUES(%s, %s, %s, %s)", resc_params)

        return redirect(url_for('auth.user_posts'))

    return render_template('auth/post.html', **context)



@bp.route('/posts', methods=('GET', 'POST'))
def user_posts():
    statement = """
            SELECT *
            FROM Posts NATURAL JOIN Category NATURAL JOIN Resource
            WHERE uid = %s
            """
    user_id = session.get('user_id')
    cursor = g.conn.execute(statement, user_id)
    res = {}
    cate = {}
    for result in cursor:
        res[result['pid']] = {
             'category_id': result['category_id'],
             'category_name': result['category_name'],
             'post_title': result['post_title'],
             'post_description': result['post_description'],
             'post_url':result['url']
        }
        cate[result['category_id']] = {
            'category_name': result['category_name']
        }


    context = dict(data = res, categories = cate)



    return render_template('auth/posts.html', **context)

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
                g.conn.execute(
                    statement,params,
                )
            except Exception as e:
                error = f"User {email} is already registered."
            if (user_type == 'agency'):
                cur = g.conn.execute('SELECT uid FROM users WHERE email = %s', (email))
                id = cur.fetchone()
                return redirect(url_for("auth.register_agency", uid = id))
            else:
                return redirect(url_for("auth.login"))
        flash(error)

    return render_template('auth/register.html')


@bp.route('/register_agency/<uid>', methods=('GET', 'POST'))
def register_agency(uid):

    # Allow user to sign up to a specific category
    cursor = g.conn.execute("SELECT * FROM Category")
    cate = {}
    for result in cursor:
        cate[result['category_id']] = {
            'category_name': result['category_name']
        }
    cursor.close()
    context = dict(category = cate)

    if request.method == 'POST':
        uid = uid[2],
        agency_type = request.form['agency_type']
        established = request.form['established']
        agency_size = request.form['agency_size']
        budget = request.form['budget']

        error = None
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
                g.conn.execute(
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
        error = None

        user = g.conn.execute(
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
    conn = get_db()
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
