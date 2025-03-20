import os, shutil, signal, sys, time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import watch
from jinja2 import Environment, FileSystemLoader
import http.server
import socketserver

SITE_NAME = "SFN"
CONTEXT = os.path.abspath('.')
CONTENT_DIR = os.path.abspath(os.path.join(CONTEXT, 'content'))
TEMPLATES_DIR = os.path.abspath(os.path.join(CONTEXT, 'templates'))
STATIC_DIR = os.path.abspath(os.path.join(CONTEXT, 'static'))
OUTPUT_DIR = os.path.abspath("./output")


env = Environment(loader=FileSystemLoader([TEMPLATES_DIR, CONTENT_DIR]))

def render_page(page_name):
    template = env.get_template(page_name)
    return template.render(site_name=SITE_NAME)

def generate_site():
    print('generating site...')
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    for filename in os.listdir(CONTENT_DIR):
        if not filename.endswith('.html'):
            continue

        print(f"generating {filename}...")
        page_content = render_page(filename)

        with open(os.path.join(OUTPUT_DIR, filename), 'w') as f:
            f.write(page_content)
    print('copying static files...')
    shutil.copytree(STATIC_DIR, os.path.join(OUTPUT_DIR, 'static'))
    print('site generated!\n\n')

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        file_path = self.translate_path(self.path)
        
        # If path doesn't exist and doesn't end with .html, try with .html extension
        if not os.path.exists(file_path) and not self.path.endswith('.html'):
            html_path = file_path + '.html'
            if os.path.exists(html_path):
                # Modify the path to include .html
                self.path = self.path + '.html'
        
        # Proceed with normal handling
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

def serve_site(port=8000):
    handler = CustomHTTPRequestHandler

    # Set the directory to serve (output directory)
    os.chdir(OUTPUT_DIR)

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving site at http://localhost:{port}\n\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('stopping server...')
            httpd.shutdown()
            httpd.server_close()
            print('server stopped\n\n')


def restart_server():
    # Generate site files and restart the server
    print("Regenerating site...")
    generate_site()
    # switching to the dir again since we deleted and recreated it
    os.chdir(OUTPUT_DIR)

def start_server_with_watch():
    # Generate the initial site
    generate_site()

    print('starting watcher...')
    watch_thread = threading.Thread(target=watch.watch, args=([CONTENT_DIR], 0.1, lambda _: restart_server()))
    watch_thread.daemon = True
    watch_thread.start()
    print('watcher started!\n\n')

    # Start the server
    serve_site()

if __name__ == "__main__":
    start_server_with_watch()


