FROM python:3.11-slim
WORKDIR /app
COPY infra/requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
ENV DJANGO_SETTINGS_MODULE=foodgram.settings
RUN python manage.py collectstatic --noinput
EXPOSE 80
CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:80 foodgram.wsgi:application"]
