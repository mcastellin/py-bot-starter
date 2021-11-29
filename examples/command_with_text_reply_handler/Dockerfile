FROM python:3.8-buster

RUN pip install --upgrade pip \
    && pip install py-bot-starter

WORKDIR /simple_bot_handler

COPY main.py .

CMD ["python", "-u", "main.py"]