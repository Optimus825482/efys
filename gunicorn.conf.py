"""Gunicorn Production Configuration for EFYS"""
import multiprocessing
import os

# Server socket
bind = os.getenv('BIND', '127.0.0.1:8000')
backlog = 2048

# Worker processes
workers = int(os.getenv('WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = os.getenv('WORKER_CLASS', 'sync')
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = int(os.getenv('TIMEOUT', 120))
keepalive = 5

# Logging
accesslog = '/var/log/efys/access.log'
errorlog = '/var/log/efys/error.log'
loglevel = os.getenv('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'efys'

# Server mechanics
daemon = False
pidfile = '/var/run/efys/gunicorn.pid'
user = None
group = None
tmp_upload_dir = None

# SSL (eğer nginx kullanmıyorsanız)
# keyfile = '/etc/ssl/private/efys.key'
# certfile = '/etc/ssl/certs/efys.crt'

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

def on_starting(server):
    """Server başlatıldığında"""
    print("EFYS starting...")

def on_reload(server):
    """Server reload edildiğinde"""
    print("EFYS reloading...")

def when_ready(server):
    """Server hazır olduğunda"""
    print("EFYS is ready. Listening on: %s" % bind)

def on_exit(server):
    """Server kapanırken"""
    print("EFYS shutting down...")
