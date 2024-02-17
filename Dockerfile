FROM python:3.11-slim-bookworm

COPY ./src/main/python .

#WORKDIR /aideas

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "main.py" ]