# @Author: Gutu, Bilal <Bilal_gutu>
# @Date:   2022-04-15T03:26:25-04:00
# @Last modified by:   Bilal_gutu
# @Last modified time: 2022-04-18T22:38:21-04:00



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
    db.close_db(g.conn)
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





@app.route('/home', methods=['GET'])
def index():
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


    context = dict(data = post, categories = cate)

    if request.method == 'GET':
        query_term = request.args.get('query_term')
        category_name = request.args.get('category')


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
        else:
            statement = """
                    SELECT *
                    FROM Posts NATURAL JOIN Category NATURAL JOIN Resource
                    """
            cursor = g.conn.execute(statement)
        res = {}
        for result in cursor:
            res[result['pid']] = {
                 'category_id': result['category_id'],
                 'category_name': result['category_name'],
                 'post_title': result['post_title'],
                 'post_description': result['post_description'],
                 'post_url':result['url']
            }


        context = dict (data = res, categories = cate)
        cursor.close()
        return render_template('index.html', **context)

    cursor.close()
    return render_template('index.html', **context)




if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8008, type=int)
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
