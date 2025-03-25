from http import HTTPStatus
from flask import Request, abort, g, jsonify, request, url_for, redirect
from flask.sessions import SecureCookieSessionInterface

from .models import LinkdingApiConnectionData
from .configuration import configuration
from .storage import storage
from flask_login import LoginManager
from flask_login import login_user as flask_login_login_user
from flask_login import login_required as flask_login_login_required
from flask_login import logout_user as flask_login_logout_user
from flask_login import current_user as flask_login_current_user
import bcrypt

login_manager = LoginManager()

def init_app(app):
    app.secret_key = configuration.secret_key
    app.session_interface = CustomSessionInterface()
    login_manager.init_app(app)
    login_manager.login_view = "bp.login"


@login_manager.user_loader
def load_user(username):
    return storage.get_user(username)

class CustomSessionInterface(SecureCookieSessionInterface):
    def save_session(self, *args, **kwargs):
        if configuration.enable_auth_proxy:
            return
        return super(CustomSessionInterface, self).save_session(*args, **kwargs)

@login_manager.request_loader
def load_user_from_request(request: Request):
    print(request.headers)
    if request.endpoint == 'integrations.get_glance_integration':
        auth_header = request.headers.get('authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            user_id = storage.get_user_id_from_glance_token(token)
            user = storage.get_user(user_id) if user_id is not None else None
            if user is not None:
                return user
        return None

    if configuration.enable_auth_proxy:
        for k, v in request.headers.items():
            if f"HTTP_{k.upper().replace('-', '_')}" != configuration.auth_proxy_username_header:
                continue
            return storage.get_or_create_user(v)
    return None

@login_manager.unauthorized_handler
def unauthorized_handler():
    if request.blueprint == 'integrations':
        abort(HTTPStatus.UNAUTHORIZED)
    return redirect(url_for('bp.login'))

def login_user(username: str, password: str):
    result = storage.get_user_and_data(username)
    if result is None:
        return False
    user, user_data = result
    if user_data.password_hash is None:
        return False
    if not bcrypt.checkpw(password.encode('utf-8'), user_data.password_hash):
        return False
    flask_login_login_user(user, remember=True)
    return True

def register_user(username: str, password: str | None = None) -> bool:
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()) if password is not None else None
    return storage.add_user(username, hashed)

def verify_password(username: str, password: str) -> bool:
    user_data = storage.get_user_data(username)
    if user_data is None:
        return False
    if user_data.password_hash is None:
        return False
    if not bcrypt.checkpw(password.encode('utf-8'), user_data.password_hash):
        return False
    return True

def change_password(username: str, password: str | None) -> bool:
    result = storage.get_user_and_data(username)
    if result is None:
        return False
    user, user_data = result
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()) if password is not None else None
    user_data.password_hash = hashed
    return storage.update_user(user, user_data)


login_required = flask_login_login_required
logout_user = flask_login_logout_user
current_user =  flask_login_current_user
