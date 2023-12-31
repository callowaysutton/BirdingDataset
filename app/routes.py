from flask import render_template, url_for, flash, redirect, session, request
from flask_login import login_user, current_user, login_required, logout_user
from flask_paginate import Pagination, get_page_args
from app import app, db, save_picture_minio
from app.models import User, Link, Bird, BirdVote
from app.forms import RegistrationForm, LoginForm, LinkForm, BirdUploadForm, BirdValidationForm
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from libgravatar import Gravatar
from sqlalchemy import func
import random, os, subprocess, tempfile, shutil

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
        "home.html",
        user=current_user,
        version=version,
    )

@app.route("/terms")
def tos():
    return render_template(
        "tos.html",
        user=current_user,
        version=version,
    )


@app.route("/about")
def about():
    return render_template("about.html", user=current_user, version=version)


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
            profile_picture=Gravatar(form.email.data).get_image(),
            email=form.email.data,
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
        "register.html", title="Register", form=form, version=version, user=current_user
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
        "login.html", title="Login", form=form, user=current_user, version=version
    )


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/upload', methods=['GET','POST'])
@login_required
def upload_bird():
    form = BirdUploadForm()
    if form.validate_on_submit():
        if 'picture' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)

        picture_data = request.files['picture']

        # Check if the file is empty
        if picture_data.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        # Ensure it's a supported file type (e.g., image)
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if not allowed_file(picture_data.filename, allowed_extensions):
            flash('Invalid file type. Supported formats are PNG, JPG, JPEG, and GIF.', 'error')
            return redirect(request.url)

        # Create a temporary directory to store the file
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, secure_filename(picture_data.filename))

        try:
            # Save the file to the temporary location
            picture_data.save(temp_path)

            # Now, you can inspect the file size
            content_length = os.path.getsize(temp_path)
            print(f"Content Length: {content_length} bytes")

            # Upload the file to Minio and get the public URL
            picture_url = save_picture_minio(temp_path)

            # Check if the picture_url is None (indicating an upload error)
            if picture_url is None:
                flash('Failed to upload the picture', 'error')
                return redirect(request.url)

            # The file is successfully uploaded, you can use the picture_url
            bird = Bird(name=request.form['name'],
                        description=request.form['description'],
                        picture_reference=picture_url,
                        latitude=float(request.form['latitude']),
                        longitude=float(request.form['longitude']),
                        user=current_user)

            db.session.add(bird)
            db.session.commit()

            flash('Your bird has been uploaded!', 'success')
            return redirect(url_for('home'))
        
        except Exception as err:
            print(f"Minio error: {err}")

        finally:
            # Delete the temporary directory and its contents
            shutil.rmtree(temp_dir, ignore_errors=True)

            flash('Your bird has been uploaded!', 'success')
            return redirect(url_for('home'))  # Redirect to the home page or a success page

    return render_template('upload.html', form=form, user=current_user, version=version)


@app.route('/validate', methods=['GET', 'POST'])
@login_required
def validate_bird():
    form = BirdValidationForm()

    # Check if a bird ID is stored in the user's session
    bird_id = session.get('bird_to_validate_id')

    if form.validate_on_submit():
        if bird_id is not None:
            bird_to_validate = Bird.query.get(bird_id)

            # Determine whether the rating is positive or negative
            if form.rating.data > 5:
                bird_to_validate.positive_votes += 1
            else:
                bird_to_validate.negative_votes += 1

            # Create a new BirdVote entry for validation
            bird_vote = BirdVote(
                bird=bird_to_validate,
                user=current_user,
                rating=form.rating.data,
                description=form.description.data
            )

            db.session.add(bird_vote)
            db.session.commit()

            flash('Thank you for your validation!', 'success')
            return redirect(url_for('home'))

    # Fetch a randomly selected bird for validation and store its ID in the session
    bird_to_validate = random.choice(Bird.query.all())
    tries = 0
    while bird_to_validate == session['bird_to_validate_id']:
        # if tries > 3:
        #     break
        bird_to_validate = random.choice(Bird.query.all())
        # tries += 1
    session['bird_to_validate_id'] = bird_to_validate.id

    return render_template('validate.html', form=form, bird_to_validate=bird_to_validate, user=current_user, version=version)

@app.route('/explore', methods=['GET'])
def explore_birds():
    # Get a list of all birds from the database
    all_birds = Bird.query.all()

    # Pagination setup
    page = request.args.get('page', type=int, default=1)
    per_page = 20
    start = (page - 1) * per_page
    end = start + per_page
    birds_to_display = all_birds[start:end]

    pagination = Pagination(
        page=page,
        per_page=per_page,
        total=len(all_birds),
        css_framework='bootstrap',
    )

    return render_template('explore.html', birds=birds_to_display, pagination=pagination, user=current_user, version=version)


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
        "dashboard/dashboard.html", user=current_user, version=version
    )


@app.route("/dashboard/create")
@login_required
def create_new():
    return render_template(
        "dashboard/create_new.html", user=current_user, version=version, form=LinkForm()
    )


@app.route("/dashboard/analytics")
@login_required
def link_analytics():
    return render_template(
        "dashboard/link_analytics.html", user=current_user, version=version
    )


@app.route("/dashboard/export")
@login_required
def export_link_data():
    return render_template(
        "dashboard/export_link_data.html", user=current_user, version=version
    )


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user, birds=Bird.query.all(), votes=BirdVote.query.all(), version=version)
