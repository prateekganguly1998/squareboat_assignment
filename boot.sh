#!/bin/bash
source venv/bin/activate
flask db upgrade
exec gunicorn -w 4 -b :$PORT --access-logfile - --error-logfile - app:app