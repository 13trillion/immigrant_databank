# @Author: Gutu, Bilal <Bilal_gutu>
# @Date:   2022-04-15T03:26:25-04:00
# @Last modified by:   Bilal_gutu
# @Last modified time: 2022-04-18T04:20:26-04:00



#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
import db, auth

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
conn = db.get_db()


app.config.from_mapping(
    SECRET_KEY='4our3yes0nly!'
)

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = db.get_db()
  except:
    print ("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


app.register_blueprint(auth.bp)

#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#

@app.route('/')
def base():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  return render_template("base.html")


# @app.route('/home')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print (request.args)


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT * FROM Posts NATURAL JOIN Category NATURAL JOIN Resource")


  post = {}
  for result in cursor:
    post[result['pid']] = {
        'category_name': result['category_name'],
        'post_title': result['post_title'],
        'post_description': result['post_description'],
        'post_url':result['url']
    }

  cursor = g.conn.execute("SELECT * FROM Category")
  cate = {}
  for result in cursor:
      cate[result['category_id']] = {
          'category_name': result['category_name']
      }
  cursor.close()



  context = dict(data = post, categories = cate)

  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at
#
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
@app.route('/another')
def another():
  return render_template("anotherfile.html")


# Example of adding new data to the database
# @app.route('/add', methods=['POST'])
# def add():
#   name = request.form['name']
#   print (name)
#   cmd = 'INSERT INTO test(name) VALUES (:name1), (:name2)';
#   g.conn.execute(text(cmd), name1 = name, name2 = name);
#   return redirect('/')


# @app.route('/search', methods=['GET', 'POST'])
@app.route('/home', methods=['GET'])
def search():
    cursor = g.conn.execute("SELECT * FROM Posts NATURAL JOIN Category NATURAL JOIN Resource")
    post = {}
    cate = {}
    for result in cursor:
      post[result['pid']] = {
          'category_id': result['category_id'],
          'category_name': result['category_name'],
          'post_title': result['post_title'],
          'post_description': result['post_description'],
          'post_url':result['url']
      }
      cate[result['category_id']] = {
          'category_name': result['category_name']
      }
    cursor.close()

    context = dict(data = post, categories = cate)

    if request.method == 'GET':
        query_term = request.args.get('query_term')
        category_name = request.args.get('category')

        db = conn
        error = None
        q = f'%{query_term}%'

        if query_term and category_name:
            statement = """
                    SELECT *
                    FROM Posts NATURAL JOIN Category NATURAL JOIN Resource
                    WHERE post_title ILIKE %s AND post_description ILIKE %s AND category_name = %s
                    """

            cursor = g.conn.execute(statement, q, q, category_name)
        elif query_term and not category_name:
            statement = """
                    SELECT *
                    FROM Posts NATURAL JOIN Category NATURAL JOIN Resource
                    WHERE post_title ILIKE %s AND post_description ILIKE %s
                    """
            cursor = g.conn.execute(statement, q, q)
        elif not query_term and category_name:
            statement = """
                    SELECT *
                    FROM Posts NATURAL JOIN Category NATURAL JOIN Resource
                    WHERE category_name = %s
                    """
            cursor = g.conn.execute(statement, category_name)
        res = {}
        for result in cursor:
            res[result['pid']] = {
                 'category_id': result['category_id'],
                 'category_name': result['category_name'],
                 'post_title': result['post_title'],
                 'post_description': result['post_description'],
                 'post_url':result['url']
            }

            print(result)
        context = dict (data = res, categories = cate)
        return render_template('index.html', **context)


    return render_template('index.html', **context)


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print ("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
