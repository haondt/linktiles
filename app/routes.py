from flask import Blueprint, Response, redirect, render_template, request, url_for
from pydantic import ValidationError

from .models import TilesSettingsRequest
from .tiles import get_tiles_configuration, update_tiles_configuration
from .authentication import login_user, login_required, logout_user, login_manager, register_user, verify_password, current_user
from .authentication import change_password as change_user_password
from .configuration import configuration
from . import linkding, linktiles_user

login_manager.login_view = "bp.login"

def add_routes(app):
    bp = Blueprint('bp', __name__, url_prefix='/') 
    if configuration.context_path is not None:
        bp = Blueprint('bp', __name__, url_prefix=configuration.context_path)
        app.config['APPLICATION_ROOT'] = configuration.context_path


    @bp.route('/', methods=['GET'])
    @login_required
    def home():
        return render_template('home.html', user='Noah')

    @bp.route('logout', methods=['GET'])
    def logout():
        if configuration.enable_auth_proxy:
            return redirect(configuration.auth_proxy_logout_url or url_for('bp.login'))
        logout_user()
        return redirect(url_for('bp.login'))

    @bp.route('change-password', methods=['GET', 'POST'])
    @login_required
    def change_password():
        if configuration.enable_auth_proxy:
            return render_template('auth_proxy_error.html')

        if request.method == 'GET':
            return render_template('change_password.html')

        old_password = request.form['old_password']
        new_password = request.form['new_password']
        new_password_confirm = request.form['new_password_confirm']

        user_id = current_user.get_id()

        if not verify_password(user_id, old_password):
            return render_template('change_password.html', error='Your old password was entered incorrectly. Please enter it again.')

        if new_password != new_password_confirm:
            return render_template('change_password.html', error='The two password fields didn\'t match.')

        if not change_user_password(user_id, new_password):
            return render_template('change_password.html', error='Unable to change password. Please try again.')

        return render_template('change_password.html', success=True)

    @bp.route('login', methods=['GET', 'POST'])
    def login():
        if configuration.enable_auth_proxy:
            return render_template('auth_proxy_error.html')

        invalid_credentials_error = "Your username and password didn't match. Please try again."
        if request.method == 'GET':
            return render_template('login.html')
        username = request.form['username']
        if not login_user(username, request.form['password']):
            return render_template('login.html', error=invalid_credentials_error, username=username), 401

        resp = Response('')
        resp.status_code = 302
        resp.headers['HX-Redirect'] = url_for('bp.home')
        return resp

    @bp.route('register', methods=['GET', 'POST'])
    def register():
        if configuration.enable_auth_proxy:
            return render_template('auth_proxy_error.html')

        if request.method == 'GET':
            return render_template('register.html')

        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return render_template('register.html', error="Passwords must match.")

        if not register_user(username, password):
            return render_template('register.html', error="Username not available.")

        if not login_user(username, password):
            return render_template('register.html', error="Encountered an error during registration. Please try again.")

        resp = Response('')
        resp.status_code = 302
        resp.headers['HX-Redirect'] = url_for('bp.home')
        return resp

    @bp.route('fragments/tag', methods=['GET'])
    @login_required
    def tag_fragment():
        return render_template('tag.html', value=request.args.get('value'))

    @bp.route('fragments/tile_configuration', methods=['GET'])
    @login_required
    def tile_configuration_fragment():
        return render_template('tile_configuration.html')

    @bp.route('settings', methods=['GET'])
    @login_required
    def settings():
        return redirect(url_for('bp.tiles_settings'))

    @bp.route('settings/tiles', methods=['GET', 'POST'])
    @login_required
    def tiles_settings():
        if request.method == 'GET':
            tiles = get_tiles_configuration(current_user.get_id())
            return render_template('tiles_settings.html', tiles=tiles)
        data = request.form['data']
        try:
            deserialized = TilesSettingsRequest.model_validate_json(data)
        except ValidationError as e:
            return render_template('tiles_settings_result.html',  validation_errors=e.errors())
        update_tiles_configuration(current_user.get_id(), deserialized.tiles)
        return render_template('tiles_settings_result.html',  success=True)

    @bp.route('settings/general', methods=['GET'])
    @login_required
    def general_settings():
        return render_template('general_settings.html')

    @bp.route('settings/integrations', methods=['GET'])
    @login_required
    def integration_settings():
        id =  current_user.get_id()
        linkding_data = linktiles_user.get_linkding_connection_data(id)
        if linkding_data is not None:
            return render_template('integration_settings.html', linkding_base_url=linkding_data.base_url)
        return render_template('integration_settings.html')

    @bp.route('settings/integrations/linkding', methods=['POST'])
    @login_required
    def linkding_integration_settings():
        base_url = request.form['base_url']
        api_key = request.form['api_key']
        success, error_message = linkding.test(base_url, api_key)
        if not success:
            message = error_message or 'Failed to connect to the linkding API.'
            return render_template('linkding_integration_settings_result.html', success=success, message=message)

        if not linktiles_user.upsert_linkding_connection_data(current_user.get_id(), base_url, api_key):
            message = "Failed to save the updated connection data. Please try again."
            return render_template('linkding_integration_settings_result.html', success=False, message=message)

        message = 'Successfully connected to the linkding API.'
        return render_template('linkding_integration_settings_result.html', success=True, message=message)

    app.register_blueprint(bp)


