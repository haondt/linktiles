from flask import Blueprint, Response, make_response, redirect, render_template, request, url_for
import random
from pydantic import ValidationError

from .models import TileColors, TileConfiguration, TileFill, TileGroupLayout, TileLayout, TileTitleLocation, TilesSettingsRequest, TimeUnit
from .tiles import create_tile, create_tiles_async, export_tiles_configuration, get_linkding_options, get_tiles_configuration, get_tiles_options, update_linkding_options, update_tiles_configuration, update_tiles_options
from .authentication import login_user, login_required, logout_user, login_manager, register_user, verify_password, current_user
from .authentication import change_password as change_user_password
from .configuration import configuration
from . import linkding, linktiles_user


def add_routes(app):
    bp = Blueprint('bp', __name__, url_prefix='/') 
    integrations_bp = Blueprint('integrations', __name__, url_prefix='/integrations/')
    if configuration.context_path is not None:
        bp.url_prefix = '/' + configuration.context_path.strip('/') + '/'
        integrations_bp.url_prefix =  '/' + configuration.context_path.strip('/') + '/integrations/'
        app.config['APPLICATION_ROOT'] = configuration.context_path

    @app.template_global()
    def randint(lower, upper):
        return random.randint(lower, upper)

    @app.template_global()
    def randseed():
        return random.random()

    @app.template_global()
    def proportional_select(value: float, values: list, distribution: list):
        s = 0
        for i, proportion in enumerate(distribution):
            s += proportion
            if value <= s:
                return values[i]
        return values[-1]

    app.jinja_env.globals['types'] = {
        TileColors.__name__: TileColors,
        TileFill.__name__: TileFill,
        TileTitleLocation.__name__: TileTitleLocation,
        TileLayout.__name__: TileLayout,
        TileGroupLayout.__name__: TileGroupLayout,
        TimeUnit.__name__: TimeUnit
    }

    @bp.route('/', methods=['GET'])
    @login_required
    def home():
        user_id = current_user.get_id()
        tiles = get_tiles_configuration(user_id)
        tiles_options = get_tiles_options(user_id)
        return render_template('home.html', tiles=tiles, options=tiles_options)

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
        return render_template('tile_configuration.html', seed=random.random())

    @bp.route('fragments/tile', methods=['GET'])
    @login_required
    def tile_fragment():
        config = TileConfiguration(
            seed=float(request.args.get('seed', 0)),
            title=request.args.get('title'),
            tags=request.args.get('tags'),
            groups=request.args.get('groups'),
            limit=int(request.args.get('limit', 100)))

        user_id = current_user.get_id()
        tile = create_tile(user_id, config)
        if isinstance(tile, str):
            return render_template("tile.html", error=tile)
        tiles_options = get_tiles_options(user_id)
        return render_template("tile.html", tile=tile, options=tiles_options)

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

    @bp.route('settings/general', methods=['GET', 'POST'])
    @login_required
    def general_settings():
        user_id = current_user.get_id()
        tiles_options = get_tiles_options(user_id)
        linkding_options = get_linkding_options(user_id)
        if request.method == 'GET':
            return render_template('general_settings.html', tiles_options=tiles_options, linkding_options=linkding_options)

        tiles_options_dirty = False
        if 'tile_colors' in request.form:
            tiles_options.colors = TileColors(request.form['tile_colors'])
            tiles_options_dirty = True
        if 'tile_fill' in request.form:
            tiles_options.fill = TileFill(request.form['tile_fill'])
            tiles_options_dirty = True
        if 'tile_title_location' in request.form:
            tiles_options.title_location = TileTitleLocation(request.form['tile_title_location'])
            tiles_options_dirty = True
        if 'tile_layout' in request.form:
            tiles_options.layout = TileLayout(request.form['tile_layout'])
            tiles_options_dirty = True
        if 'tile_width' in request.form:
            tiles_options.width = int(request.form['tile_width'])
            tiles_options_dirty = True
        if 'tile_group_layout' in request.form:
            tiles_options.group_layout = TileGroupLayout(request.form['tile_group_layout'])
            tiles_options_dirty = True

        linkding_options_dirty = False
        if 'linkding_cache_enabled' in request.form:
            linkding_options.cache_enabled = request.form['linkding_cache_enabled'].lower() == "true"
            linkding_options_dirty = True
        if 'linkding_cache_duration' in request.form:
            linkding_options.cache_duration = float(request.form['linkding_cache_duration'])
            linkding_options_dirty = True
        if 'linkding_cache_duration_unit' in request.form:
            linkding_options.cache_duration_unit = TimeUnit(request.form['linkding_cache_duration_unit'])
            linkding_options_dirty = True

        if tiles_options_dirty:
            update_tiles_options(user_id, tiles_options)

        if linkding_options_dirty:
            update_linkding_options(user_id, linkding_options)

        return ''

    @bp.route('settings/integrations', methods=['GET'])
    @login_required
    def integration_settings():
        id =  current_user.get_id()
        kwargs = {}
        linkding_data = linktiles_user.get_linkding_connection_data(id)
        if linkding_data is not None:
            kwargs['linkding_base_url'] = linkding_data.base_url

        kwargs['glance_token'] = linktiles_user.get_glance_token(id)
        return render_template('integration_settings.html', **kwargs)

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

    @bp.route('settings/tiles/download')
    def download_tiles_configuration():
        configuration = export_tiles_configuration(current_user.get_id())
        response = make_response(configuration.model_dump_json())
        response.headers["Content-Type"] = "application/json"
        response.headers["Content-Disposition"] = "attachment; filename=linktiles.json"
        return response

    @integrations_bp.route('glance', methods=['GET'])
    @login_required
    async def get_glance_integration():
        user_id = current_user.get_id()
        tiles = await create_tiles_async(user_id)
        if isinstance(tiles, str):
            rendered = render_template('glance.html', error=tiles)
        else:
            tiles_options = get_tiles_options(user_id)
            rendered = render_template('glance.html', tiles=tiles, options=tiles_options)

        response = make_response(rendered)
        response.headers['Widget-Title'] = 'linktiles'
        response.headers['Widget-Content-Type'] = 'html'
        response.headers['Content-Type'] = 'text/html'
        response.headers['Widget-Content-Frameless'] = 'true'
        return response

    @bp.route('settings/integrations/glance/rotate_token', methods=['POST'])
    @login_required
    def glance_rotate_token():
        id =  current_user.get_id()
        new_token = linktiles_user.rotate_glance_token(id)
        return render_template('integration_settings_glance_api_key.html', value=new_token)


    app.register_blueprint(bp)
    app.register_blueprint(integrations_bp)


