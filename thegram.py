import asyncio
import logging
import sys
from dataclasses import dataclass
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, \
    MessageHandler, filters, TypeHandler

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

CHAT_ID = 50877378


@dataclass
class MyMessageUpdate:
    msg: str


async def my_message_update(
        update: MyMessageUpdate,
        context: ContextTypes.DEFAULT_TYPE
) -> None:
    await context.bot.send_message(
        chat_id=CHAT_ID,
        text=update.msg
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("START")
    print(update)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello, World. I will only talk to a single chat."
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("CANCEL")
    print(update)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Bye."
    )


async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("ON MESSAGE")
    print(update)
    print(update.effective_chat.id)


async def main():
    try:
        token = os.environ["TOKEN"]
    except KeyError:
        print("Pass Telegram TOKEN as environment variable.", file=sys.stderr)
        sys.exit(1)

    application = ApplicationBuilder().token(token).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    cancel_handler = CommandHandler('cancel', cancel)
    application.add_handler(cancel_handler)

    message_handler = MessageHandler(
        filters.TEXT & (~filters.COMMAND),
        on_message
    )
    application.add_handler(message_handler)

    application.add_handler(
        TypeHandler(type=MyMessageUpdate, callback=my_message_update)
    )

    async with application:
        await application.start()
        await application.update_queue.put(
            MyMessageUpdate(msg="MY PROACTIVE MESSAGE")
        )
        await asyncio.sleep(5)
        await application.stop()


if __name__ == '__main__':
    asyncio.run(main())
