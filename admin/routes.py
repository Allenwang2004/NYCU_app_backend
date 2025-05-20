from flask import Blueprint, request, redirect, render_template, session, url_for, current_app

bp = Blueprint("admin_auth", __name__)

@bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if email == current_app.config["ADMIN_EMAIL"] and password == current_app.config["ADMIN_PASSWORD"]:
            session["admin_logged_in"] = True
            return redirect("/admin/")
        return "登入失敗，請確認帳號密碼", 403
    return render_template("admin_login.html")

@bp.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_auth.admin_login"))