from flask import render_template, redirect, flash, session, request, url_for
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename
from loguru import logger

from .app import app
from .email import send_verification_email
from .security import generate_confirmation_token, confirm_token
from .login import load_user
from .utils import change_password, get_all_videos_of_user, get_user_by_username, is_email_unique, is_username_unique, get_video_by_id, create_new_user, create_new_video, get_all_videos, \
    get_user_by_email, does_username_exists



@app.route("/", methods=["GET", "POST"])
def index():
    videos = get_all_videos()
    return render_template("main.html", videos=videos)


@app.route("/signUp", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        if not (request.form["username"] and request.form["email"] and request.form["password1"] and request.form["password2"]):
            flash("Fill in all input fields", category="error")
        elif not len(request.form["email"]) > 5 and "@" not in request.form["email"]:
            flash("Enter a valid email", category="error")
        elif request.form["password1"] != request.form["password2"]:
            flash("Passwords don't match", category="error")
        elif len(request.form["password1"]) < 7:
            flash("Password must be at least 7 characters long", category="error")
        elif is_email_unique(request.form["email"]):
            flash("User with this email already exists", category="error")
        elif is_username_unique(request.form["username"]):
            flash("User with this username already exists", category="error")
        else:
            try:
                password_hash = generate_password_hash(request.form["password1"])
                session["email"] = request.form["email"]
                session["username"] = request.form["username"]
                session["hpsw"] = password_hash

                token = generate_confirmation_token(request.form["email"])
                send_verification_email(target=request.form["email"], link=url_for("confirm_registration", token=token, _external=True))
                flash("Successfully sent verification mail", category="success")
            except Exception as ex:
                logger.error(ex)

    return render_template("sign_up.html", title="Sign up")


@app.route("/signIn", methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        user = get_user_by_email(request.form["email"])
        if not (request.form["email"] and request.form["password"]):
            flash("Fill in all input fields", category="error")

        elif not user:
            flash("User with this email doesn't exist", category="error")

        elif not check_password_hash(user.hpsw, request.form["password"]):
            flash("Invalid password", category="error")

        else:
            if check_password_hash(user.hpsw, request.form["password"]):
                login_user(user)
                logger.info(f"The user {user.username} has logged in")
                return redirect(url_for("profile"))

    return render_template("sign_in.html", title="Sign in")


@app.get("/confirmRegistration/<token>")
def confirm_registration(token: str):
    try:
        email = confirm_token(token)
    except:
        flash("The confirmation link is invalid or has expired", "error")
    if email == session["email"]:  
        user = create_new_user(session["username"], session["email"], session["hpsw"])
        session.clear()
        logger.info(f"The user {user.username} has signed up")
        return redirect(url_for("sign_in"))
    else:
        flash("The confirmation link is invalid or has expired", "error")
    return render_template("confirm_registration.html")


@app.route("/resetPassword", methods=["GET", "POST"])
def password_recovery():
    if request.method == "POST":
        if not request.form["email"]:
            flash("Fill in all input fields", category="error")
        else: 
            if does_username_exists(request.form["email"]):
                token = generate_confirmation_token(request.form["email"])
                send_verification_email(target=request.form["email"], link=url_for("makeNewPassword", token=token, _external=True))
                flash("Successfully sent verification mail", category="success")
            else:
                flash("User with this email doesn't exist", category="error")

    return render_template("reset_password.html")


@app.route("/makeNewPassword/<token>", methods=["GET", "POST"])
def makeNewPassword(token: str):
    try:
        email = confirm_token(token)
        if request.method == "POST":
            if not (request.form["password1"] and request.form["password2"]):
                flash("Fill in all input fields", category="error")
            elif request.form["password1"] != request.form["password2"]:
                flash("Passwords don't match", category="error")
            elif len(request.form["password1"]) < 7:
                flash("Password must be at least 7 characters long", category="error")
            else:
                try:
                    hash = generate_password_hash(request.form["password1"])
                    user = change_password(email, hash)
                    flash("Password succesfully changed", category="success")
                    logger.info(f"{user.username} successfully changed password")
                    return redirect(url_for("sign_in"))  
                except Exception as ex:
                    logger.error(f"{ex} occured while user {user.username} was trying to change his password")
                    return redirect(url_for("index")) 

        return render_template("make_new_password.html", confirmed=True, token=token)
    except:
        flash("The confirmation link is invalid", category="error")
        return render_template("make_new_password.html", confirmed=False)


@app.route("/myProfile", methods=["GET", "POST"])
def profile():
    if not current_user.is_authenticated:
        return redirect(url_for("sign_in"))
    if request.method == "POST":
        if not (request.files["videofile"] and request.form["title"]):
            flash("Fill in all input fields", category="error")
        else:
            try:
                path = "static/videos/" + secure_filename(request.form["title"]).lower() + ".mp4"
                video = request.files["videofile"]
                video.save("flask_app/" + path)
                video_title = request.form["title"]
                author = current_user.username
                create_new_video(video_title, author, path)
            except RequestEntityTooLarge:
                flash("Video size mustn't exceed 32 mb", category="error")
            except FileNotFoundError:
                flash("Something went wrong, try again :(", category="error")
            except Exception as ex:
                logger.error(f"{ex} occured while uploading video")
                flash("Something went wrong, try again :(", category="error")
    
    videos = get_all_videos_of_user(current_user.username)
    return render_template("my_profile.html", videos=videos)


@app.get("/like/<int:video_id>/<action>")
@login_required
def like_action(video_id: int, action: str):
    video = get_video_by_id(video_id)
    if action == "like":
        current_user.like_video(video)
    if action == "unlike":
        current_user.unlike_video(video)
    return redirect(request.referrer)


@app.get("/myLikes")
@login_required
def show_my_likes():
    videos = current_user.show_user_likes()
    return render_template("my_likes.html", videos=videos)


@app.get("/video/<int:id>")
def show_video_page(id: int):
    video = get_video_by_id(id)
    return render_template("video.html", video=video)


@app.get("/users/<username>")
def show_user_page(username: str):
    if current_user.is_authenticated and current_user.username == username:
        return redirect(url_for("profile"))
    user = get_user_by_username(username)
    videos = get_all_videos_of_user(user.username)
    return render_template("user_page.html", user=user, videos=videos)


@app.get("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("sign_in"))


@app.get("/deleteVideo/<int:id>")
@login_required
def delete_video(id):
    video = get_video_by_id(id)
    if current_user.username != video.author:
        return redirect(request.referrer)
    video.delete_video()
    return redirect(request.referrer)


@app.errorhandler(404)
def handle_error404(error):
    return render_template("error404.html")