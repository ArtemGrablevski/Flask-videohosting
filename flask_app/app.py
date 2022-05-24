from flask import Flask
from flask_migrate import Migrate
from .models import db
import settings


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(settings.Config)
    register_extensions(app)
    return app

def register_extensions(app: Flask) -> None:
    db.init_app(app)
    migrate = Migrate(app, db)


app = create_app()



