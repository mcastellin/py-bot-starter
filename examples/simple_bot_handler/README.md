# Simple Bot Handler

The example in this directory shows how you can implement a bot command handler

## How to run this example

To run the bot you'll need a valid `BOT_TOKEN` that you can obtain from Telegram's BotFather and a running
MongoDB instance.

1. Run an instance of MongoDB with Docker:
    ```bash
    docker run -d --name mongodb -p 27017:27017 mongo
    ```

2. Export your BOT_TOKEN as an environment variable:
    ```bash
    export BOT_TOKEN="<your bot token>"
    ```
    or on Windows:
    ```bash
    set BOT_TOKEN="<your bot token>"
    ```

3. Install py-bot-starter and run the example:
    ```bash
    pip install py-bot-starter
    python main.py
    ```