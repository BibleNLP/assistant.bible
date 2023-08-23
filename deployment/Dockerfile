FROM python:3.10

COPY ./app /app/app
COPY ./requirements.txt requirements.txt
RUN mkdir /app/logs
RUN pip install --no-cache-dir --upgrade -r requirements.txt
WORKDIR /app/app

CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8000"]
