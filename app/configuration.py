import os

DEFAULT_SECRET_KEY = 'iObhCvcRE3H2Oiy77MKzl2x5+NhO/V6e6Xp1GqJlwQA='

def parse_bool_env_var(var_name, default=False):
    """Convert an environment variable to a boolean value.
    
    Returns True if value is 'true', '1', or any non-zero number (case-insensitive).
    Returns False for 'false', '0', None, or any other value.
    
    Args:
        var_name (str): Name of the environment variable to parse
        default (bool): Default value if variable is not set (default: False)
    
    Returns:
        bool: Parsed boolean value
    """
    value = os.getenv(var_name)
    if value is not None:
        value_str = str(value).lower()
        return value_str in ('true', '1') or \
               (value_str.isdigit() and int(value_str) != 0)
    return default

class Config:
    def __init__(self):
        self.enable_auth_proxy = parse_bool_env_var('LT_ENABLE_AUTH_PROXY')
        self.auth_proxy_username_header = os.getenv('LT_AUTH_PROXY_USERNAME_HEADER', 'HTTP_REMOTE_USER')
        self.auth_proxy_logout_url = os.getenv('LT_AUTH_PROXY_LOGOUT_URL', None)
        self.secret_key = os.getenv('LT_SECRET_KEY', DEFAULT_SECRET_KEY)
        self.is_development = os.getenv('LT_ENVIRONMENT', 'prod') in ['dev', 'development']
        self.context_path = os.getenv('LT_CONTEXT_PATH', None)
        self.server_port = int(os.getenv('LT_SERVER_PORT', 5001))

        self.db_engine = os.getenv('LT_DB_ENGINE', 'memory')
        if self.db_engine not in ['memory', 'redis']:
            self.db_engine = 'memory'
        self.db_host = os.getenv('LT_DB_HOST', 'localhost')
        self.db_user = os.getenv('LT_DB_USER', 'linktiles')
        self.db_password = os.getenv('LT_DB_PASSWORD', None)
        db_port = os.getenv('LT_DB_PORT', None)
        if db_port is not None:
            self.db_port = int(db_port)
        else:
            self.db_port = None
        if self.db_engine == 'redis' and self.db_port is None:
            self.db_port = 6379


configuration = Config()
