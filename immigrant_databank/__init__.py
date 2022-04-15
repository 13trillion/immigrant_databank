# @Author: Gutu, Bilal <Bilal_gutu>
# @Date:   2022-04-14T23:14:22-04:00
# @Last modified by:   Bilal_gutu
# @Last modified time: 2022-04-15T00:45:57-04:00



import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'immigrant_databank.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return '<h1>Welcome, to International Immigrant Databank!</h1>'

    return app
