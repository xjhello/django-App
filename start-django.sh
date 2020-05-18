#!/bin/sh
source venv/bin/activate
exec gunicorn -w 4 -b 0.0.0.0:8001 ros.wsgi --log-level=info