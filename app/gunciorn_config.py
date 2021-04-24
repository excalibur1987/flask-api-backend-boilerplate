import os

bind = "unix:///tmp/nginx.socket"
workers = int(os.getenv("GUNICORN_WORKERS", str(os.cpu_count() or 1))) * 2
