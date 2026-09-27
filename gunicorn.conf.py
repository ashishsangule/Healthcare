import os

# Bind to 0.0.0.0 with Render's dynamic PORT environment variable (default 10000)
port = os.environ.get("PORT", "10000")
bind = f"0.0.0.0:{port}"

# Concurrency and timeout configuration
workers = int(os.environ.get("WEB_CONCURRENCY", "2"))
threads = int(os.environ.get("PYTHON_GET_THREADS", "4"))
timeout = 120

# Standard output logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
