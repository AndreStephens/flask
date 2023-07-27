import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, 
    session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        
        # Validate that username and password are not empty
        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        
        # If no error, insert new user data in database
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                # redirect to login page
                return redirect(url_for("auth.login"))
            
        flash(error)
        
    return render_template('auth/register.html')


@bp.route("/login", methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()
        
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
            
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        
        flash(error)
        
    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    """
    Registers a function that runs before the view function, no matter the URL requested. `load_logged_in_user` checks if a user id is stored in the session and gets that user’s data from the database, storing it on g.user, which lasts for the length of the request. If there is no user id, or if the id doesn’t exist, `g.user` will be None.
    """
    user_id = session.get('user_id')
    
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            "SELECT * FROM user WHERE id = ?", (user_id,)
        ).fetchone()
        
        
@bp.route('/logout')
# Remove user id from session
def logout():
    session.clear()
    return redirect(url_for('index'))


# Creating, editing, and deleting blog posts will require a user to be logged in. A decorator can be used to check this for each view it’s applied to.
def login_required(view):
    """
    Returns a new view function that wraps the original view it’s applied to. The new function checks if a user is loaded and redirects to the login page otherwise. If a user is loaded the original view is called and continues normally.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrapped_view