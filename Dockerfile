FROM python:3.11-slim-bookworm

COPY src/python/main .

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "main.py" ]