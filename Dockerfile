# syntax=docker/dockerfile:1
FROM python:3.7-alpine
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


WORKDIR /code
RUN apk --version
RUN apk add postgresql-dev gcc python3-dev musl-dev
COPY requirements.txt /code/
RUN pip3 install -r requirements.txt
EXPOSE 8000
COPY . /code/
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
