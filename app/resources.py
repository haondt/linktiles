import requests
import atexit

http_session = requests.Session()

@atexit.register
def cleanup():
    http_session.close()
