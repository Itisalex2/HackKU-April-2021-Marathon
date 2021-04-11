import cs50
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from functools import wraps
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import random


# Connecting to the database
db = cs50.SQL("sqlite:///storage.db")

# Adding/removing users table
# db.execute(
#     "CREATE TABLE users (ID INTEGER PRIMARY KEY, username TINYTEXT NOT NULL, HASH TEXT NOT NULL);"
# )
# db.execute("DROP TABLE users")

# Insert into users table
# db.execute("INSERT INTO users (username, hash) VALUES (:username, :password_hash)",
#            username="hi", password_hash=generate_password_hash("password"))

# Adding/removing photos table
# db.execute(
#     "CREATE TABLE photos (username TINYTEXT NOT NULL, photo_url TEXT)"
# )
# db.execute("DROP TABLE photos")

# Insert into photos table
# db.execute("INSERT INTO photos (username, photo) VALUES (:username, :password_hash)",
#            username="hi", password_hash="ae2ewaf2sds")

# Deleting anything
# db.execute("DELETE FROM users WHERE ID = 2")

# Actual program

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(string):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            string = string.replace(old, new)
        return string
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
@login_required
def index():
    """ Homepage """
    user_id = session["user_id"]
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["HASH"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["ID"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        # Define the length of the username row to check if the username is already present
        row_length = db.execute(
            "SELECT username FROM users WHERE username = :username", username=request.form.get("username"))
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Ensure passwords match
        elif request.form.get("password") != request.form.get("confirmation_password"):
            return apology("Passwords do not match", 403)
        # Ensure the username hasn't been taken
        elif len(row_length) != 0:
            return apology("Username already taken", 403)
        else:
            db.execute("INSERT INTO users (username, HASH) VALUES (:username, :password_hash)", username=request.form.get(
                "username"), password_hash=generate_password_hash(request.form.get("password")))
            # Remember which user has logged in
            rows = db.execute("SELECT * FROM users WHERE username = :username",
                              username=request.form.get("username"))
            session["user_id"] = rows[0]["ID"]
            return redirect("/")


@app.route("/corners")
def corners():
    """ Load bouncing images """
    random_url = randomise_image()
    return render_template("corners.html", random_url=random_url)


@app.route("/spin")
def spin():
    """ Load spinning images """
    random_url = randomise_image()
    return render_template("spin.html", random_url=random_url)


@app.route("/filters")
def filters():
    """ Load filtered images """
    random_url = randomise_image()
    return render_template("filters.html", random_url=random_url)


@app.route("/input", methods=["GET", "POST"])
def input():
    """ Allowing the user to input url's """
    # Taking the input data from html
    link_array = []
    tempString = ""
    request_array = request.form.get("links_array")
    for pos, value in enumerate(request_array):
        if value == ",":
            link_array.append((tempString))
            tempString = ""
        else:
            tempString += str(value)
    link_array.append(tempString)
    # Figuring out who is the current user
    user = db.execute("SELECT * FROM users WHERE ID = :ID",
                      ID=session["user_id"])
    # Entering the data into the database
    for link in link_array:
        db.execute("INSERT INTO photos (username, photo_url) VALUES (:username, :photo_url)",
                   username=user[0]["username"], photo_url=link)
    return redirect("/")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


def randomise_image():
    # Figuring out who is the current user
    user = db.execute("SELECT * FROM users WHERE ID = :ID",
                      ID=session["user_id"])
    urls = db.execute("SELECT photo_url FROM photos WHERE username = :username",
                      username=user[0]["username"])
    random_number = random.randint(0, len(urls) - 1)
    random_url = urls[random_number]["photo_url"]
    return random_url


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
    app.debug = True
    app.run()
