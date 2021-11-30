FROM python:3.8-buster

RUN pip install --upgrade pip \
    && pip install py-bot-starter

WORKDIR /render_inline_keyboard_markup

COPY main.py .

CMD ["python", "-u", "main.py"]