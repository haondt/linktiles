from . import linktiles
from .configuration import configuration

app = linktiles()
app.run(debug=configuration.is_development, port=configuration.server_port)
