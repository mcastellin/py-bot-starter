FROM python:3.8-buster

RUN pip install --upgrade pip \
    && pip install py-bot-starter

WORKDIR /command_with_text_reply_handler

COPY main.py .

CMD ["python", "-u", "main.py"]