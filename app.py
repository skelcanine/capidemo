import os
from flask import Flask, render_template
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import Config
from models import db, User

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(str(user_id))

    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.capillaroscopy import capillaroscopy_bp

    limiter.limit("10 per minute")(auth_bp)
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(capillaroscopy_bp)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', error_message="Page Not Found"), 404

    with app.app_context():
        db.create_all()
        seed_admin_user()

    return app

def seed_admin_user():
    admin_email = Config.ADMIN_EMAIL
    admin_full_name = Config.ADMIN_FULL_NAME
    admin_password = Config.ADMIN_PASSWORD
    
    existing_admin = User.query.filter_by(email=admin_email).first()
    if not existing_admin:
        admin = User(
            full_name=admin_full_name,
            email=admin_email,
            role='admin',
            credits=9999
        )
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        print(f"[+] Admin account created: Email='{admin_email}' Name='{admin_full_name}'")
    else:
        if existing_admin.role != 'admin':
            existing_admin.role = 'admin'
            db.session.commit()

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
