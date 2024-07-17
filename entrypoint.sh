#!/bin/bash
# entrypoint.sh

set -e

# Function to wait for the database to be ready
wait_for_db() {
  echo "Waiting for database to become available..."
  while ! nc -z $DJANGO_DATABASE_HOST $DJANGO_DATABASE_PORT; do
    sleep 1
  done
  echo "Database is available"
}

# Call the function to ensure DB is ready
wait_for_db

# Apply specific app migrations
echo "Applying ytauser migrations..."
python manage.py makemigrations ytauser || { echo 'Failed to make migrations for ytauser'; exit 1; }
python manage.py makemigrations yta_app || { echo 'Failed to make migrations for ytau_app'; exit 1; }

echo "Applying migrations..."
python manage.py migrate --noinput || { echo 'Failed to apply migrations'; exit 1; }

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input --clear || { echo 'Failed to collect static files'; exit 1; }

# Start the server
echo "Starting Kafka consumer..."
# exec python manage.py runserver 0.0.0.0:8000
# nohup python manage.py runserver 0.0.0.0:8000 > yta_log.log &
nohup python kafka/consumer.py > media/logs/consumer.log &

echo "Starting Django development server..."
python manage.py runserver 0.0.0.0:8000