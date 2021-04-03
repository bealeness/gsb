from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from gsb.config import Config


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'main.home'
login_manager.login_message_category = 'info'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from gsb.main.routes import main
    from gsb.admin.routes import admin
    from gsb.term.routes import term
    from gsb.bond.routes import bond
    from gsb.errors.handlers import errors
    app.register_blueprint(main)
    app.register_blueprint(admin)
    app.register_blueprint(term)
    app.register_blueprint(bond)
    app.register_blueprint(errors)

    return app
