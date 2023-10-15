from flask import render_template, url_for, flash, redirect
from flask_login import login_user, current_user, login_required, logout_user
from app import app, db
from app.models import User, Link
from app.forms import RegistrationForm, LoginForm, LinkForm
from werkzeug.security import generate_password_hash, check_password_hash
from libgravatar import Gravatar
from sqlalchemy import func
import subprocess

# Get the current version
git_command = ["git", "rev-parse", "--short", "HEAD"]
version = ""

try:
    # Run the Git command
    result = subprocess.run(
        git_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    if result.returncode == 0:
        # Successfully retrieved the HEAD hash
        head_hash = result.stdout.strip()
        version = head_hash
    else:
        # There was an error running the Git command
        print("Error:", result.stderr)
except FileNotFoundError:
    # Git executable not found
    print("Git is not installed or not in the system's PATH.")
    version = "N/A"
except Exception as e:
    # Handle other exceptions
    print("An error occurred:", str(e))


@app.route("/")
def home():
    return render_template(
        "home.jinja",
        user=current_user,
        version=version,
        user_count=db.session.query(func.count()).select_from(User).scalar(),
        total_visits=db.session.query(func.count()).select_from(User).scalar(),
        visits_day=db.session.query(func.count()).select_from(User).scalar(),
        total_links=db.session.query(func.count()).select_from(Link).scalar(),
    )


@app.route("/about")
def about():
    return render_template("about.jinja", user=current_user, version=version)


@app.route("/register", methods=["GET", "POST"])
def register():
    # Why would you be here otherwise??
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = RegistrationForm()
    # Passwords do not match...
    if form.password.data != form.confirm_password.data:
        flash("Your passwords did not match!", "danger")
        return redirect(url_for("register"))

    if form.validate_on_submit():
        # Hash the user's password and create a new User instance
        hashed_password = generate_password_hash(form.password.data, method="scrypt")
        new_user = User(
            username=form.username.data,
            password=hashed_password,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            organization=form.organization.data,
            profile_picture=Gravatar(form.email.data).get_image(),
            # phone_number=form.phone_number.data,
            email=form.email.data,
            location=form.location.data,
            # website=form.website.data,
            # interests=form.interests.data,
            # bio=form.bio.data
        )

        # Add the new user to the database
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Your account has been created! You can now log in.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            db.session.rollback()  # Rollback changes in case of an error
            flash(
                "An error occurred while creating your account. Please try again later.",
                "danger",
            )
            print(e)  # Print the error for debugging
            return redirect(url_for("register"))
    # else:
    #     flash('Username taken or passwords did not match!', 'danger')
    return render_template(
        "register.jinja", title="Register", form=form, version=version
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    # Why would you be here otherwise??
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        # Check if the user exists and the password is correct
        if user and check_password_hash(user.password, form.password.data):
            # Set the user session
            login_user(user)
            flash("Login successful!", "success")
            # You can implement a session-based login system here if needed
            return redirect(url_for("home"))
        else:
            flash(
                "Login unsuccessful. Please check your username and password.", "danger"
            )

    return render_template(
        "login.jinja", title="Login", form=form, user=current_user, version=version
    )


@app.route("/logout")
@login_required  # Ensure that only logged-in users can log out
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template(
        "dashboard/dashboard.jinja", user=current_user, version=version
    )


@app.route("/dashboard/create")
@login_required
def create_new():
    return render_template(
        "dashboard/create_new.jinja", user=current_user, version=version, form=LinkForm()
    )


@app.route("/dashboard/analytics")
@login_required
def link_analytics():
    return render_template(
        "dashboard/link_analytics.jinja", user=current_user, version=version
    )


@app.route("/dashboard/export")
@login_required
def export_link_data():
    return render_template(
        "dashboard/export_link_data.jinja", user=current_user, version=version
    )


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.jinja", user=current_user, version=version)
