from flask_login import LoginManager
from .app import app
from .models import UserModel


login_manager = LoginManager(app)
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id: int):
    return UserModel.query.get(int(user_id))
