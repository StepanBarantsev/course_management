worker: python telegram/chat/main.py
web: flask db upgrade --directory=web/migrations; gunicorn --chdir web server:app