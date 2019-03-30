FROM python:3-alpine
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
CMD ["python3", "manage.py", "makemigrations"]
CMD ["python3", "manage.py", "migrate", "--run-syncdb"]
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
