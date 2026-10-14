"""Ntuthuko Workforce - Flask application factory."""
from datetime import timedelta
from flask import Flask, render_template_string
from config import Config
from database import close_db, init_db
from ui import fmt_hours
import auth


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)
    if config:
        app.config.update(config)

    init_db(app)
    app.teardown_appcontext(close_db)
    app.before_request(auth.load_user)
    app.before_request(auth.check_csrf)
    app.jinja_env.globals["csrf_token"] = auth.csrf_token
    app.jinja_env.filters["hm"] = fmt_hours

    from pages import BLUEPRINTS
    for bp in BLUEPRINTS:
        app.register_blueprint(bp)

    @app.after_request
    def headers(resp):
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Referrer-Policy"] = "same-origin"
        return resp

    @app.errorhandler(403)
    @app.errorhandler(404)
    @app.errorhandler(400)
    def error(e):
        from layout import render_page
        from flask import g
        msg = {403: "You do not have permission to open this page.",
               404: "That page does not exist.", 400: getattr(e, "description", "Bad request.")}[e.code]
        if not getattr(g, "settings", None):
            return msg, e.code
        from markupsafe import Markup, escape
        body = Markup("<p class='empty'>") + escape(msg) + Markup("</p><p><a class='btn' href='/'>Back to dashboard</a></p>")
        return render_page(f"Error {e.code}", body), e.code

    return app
