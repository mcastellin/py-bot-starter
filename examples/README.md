# Py-Bot-Starter Sample Projects

This directory contains several sample projects to showcase different `py-bot-starter` features. You can use these
examples to learn how to use the framework, or even as templates to setup your own bot project! 🚀

## How to run this example

To run the bot you'll need a valid `BOT_TOKEN` that you can obtain from
Telegram's [BotFather](https://telegram.dog/BotFather).

1. Export your BOT_TOKEN as an environment variable:
    ```bash
    export BOT_TOKEN="<your bot token>"
    ```
   or on Windows:
    ```bash
    set BOT_TOKEN="<your bot token>"
    ```

2. Move into the root directory of the sample project you want to run, for example:
   ```bash
   cd examples/simple_bot_handler
   ```

4. Change into the sample project root directory, and run the example with Docker compose:
    ```bash
    docker-compose up --build
    ```

5. When you are done testing, you can remove all traces of the application with the following command:
   ```bash
   docker-compose down -v --rmi local
   ```

## Available sample projects

- [Simple Bot Handler](simple_bot_handler): A simple bot that can echo a message back to the user
- [Text Reply Bot Handler](command_with_text_reply_handler): Yet another echo bot that waits for the user to send the
  message to echo
- [Keyboard Markups](render_inline_keyboard_markup): Select your current mood from an inline keyboard rendered by the
  bot and get a motivational quote