FROM python:3.10.13-slim

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /bot
WORKDIR /bot

ENV PYTHONPATH=.

CMD [ "python", "bot/main.py" ]