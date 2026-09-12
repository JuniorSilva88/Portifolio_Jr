# Procfile — usado por plataformas que leem esse padrão (Render, Railway, Heroku).
# Mantenho aqui como alternativa ao startCommand do render.yaml.
web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 60
release: python manage.py migrate --noinput
