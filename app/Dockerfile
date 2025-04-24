# app/Dockerfile

FROM python:3.11-slim

WORKDIR /code

COPY . /code/app

RUN pip install --no-cache-dir -r /code/app/requirements.txt

ENV IS_CLOUD_ENV=false
ENV PORT=8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]