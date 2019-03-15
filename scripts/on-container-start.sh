# Create db migrations
python manage.py  makemigrations

# Provision changes to db
python manage.py migrate

# Load static files
python manage.py collectstatic --noinput

# Load the demo configuration
python demo.py

# Start gunicorn server and enabled hot reload
gunicorn --reload activflow.wsgi:application -b 0.0.0.0:8000