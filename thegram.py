import asyncio
import logging
import os
import signal
import sys
from dataclasses import dataclass

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, \
    MessageHandler, filters, TypeHandler, Application

from sysloghandler import SyslogHandler, Message

# GLOBAL SETTINGS #
CHAT_ID = 50877378
VERSION = "0.1.0"
###################

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

application: Application


@dataclass
class MyMessage:
    msg: str
    notification: bool


async def on_my_message(
        msg: MyMessage,
        context: ContextTypes.DEFAULT_TYPE
) -> None:
    await context.bot.send_message(
        chat_id=CHAT_ID,
        text=msg.msg,
        disable_notification=not msg.notification,
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


def raise_system_exit():
    raise SystemExit


async def alert(msg: Message):
    print(f"ALERT {msg}")

    await application.update_queue.put(
        MyMessage(msg=msg.msg2 or msg.msg,
                  notification=True)
    )


async def info(msg: Message):
    print(f"INFO {msg}")

    await application.update_queue.put(
        MyMessage(msg=msg.msg2 or msg.msg,
                  notification=False)
    )


async def main():
    try:
        token = os.environ["TOKEN"]
    except KeyError:
        print("Pass Telegram TOKEN as environment variable.", file=sys.stderr)
        sys.exit(1)

    global application
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
        TypeHandler(type=MyMessage, callback=on_my_message)
    )

    loop = asyncio.get_event_loop()

    async with application:
        handler = SyslogHandler()
        handler.info = info
        handler.alert = alert
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: handler,
            local_addr=("0.0.0.0", 12312)
        )
        await application.start()
        await application.update_queue.put(
            MyMessage(msg=f"Starting SyslogHandler v{VERSION}",
                      notification=True)
        )
        stop_signals = (signal.SIGINT, signal.SIGTERM, signal.SIGABRT)
        for sig in stop_signals or []:
            loop.add_signal_handler(sig, raise_system_exit)

        loop.run_forever()
        await application.stop()
        transport.close()


if __name__ == '__main__':
    global_loop = asyncio.get_event_loop()
    main_task = asyncio.ensure_future(main())
    global_loop.run_forever()
