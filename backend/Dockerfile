FROM python:3.14-slim

WORKDIR /app

# Install system deps including audio deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential pkg-config libasound2-dev

COPY . /app

RUN pip install --upgrade pip
RUN pip install .

EXPOSE 8000
ENV DJANGO_SETTINGS_MODULE="einsingen_django.settings"

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
