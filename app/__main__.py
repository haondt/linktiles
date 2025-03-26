from . import linktiles
from .configuration import configuration

linktiles.run(debug=configuration.is_development, port=configuration.server_port)
