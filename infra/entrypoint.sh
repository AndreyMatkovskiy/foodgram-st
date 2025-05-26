until pg_isready -h db -U $POSTGRES_USER -d $POSTGRES_DB; do
  sleep 2
done
python manage.py migrate
python manage.py runserver 0.0.0.0:8000