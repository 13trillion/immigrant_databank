# @Author: Gutu, Bilal <Bilal_gutu>
# @Date:   2022-04-15T15:30:36-04:00
# @Last modified by:   Bilal_gutu
# @Last modified time: 2022-04-15T15:30:49-04:00
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

# from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')
