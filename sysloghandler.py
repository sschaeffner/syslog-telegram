import asyncio
import socketserver
from asyncio import DatagramProtocol
from dataclasses import dataclass


@dataclass
class Message:
    pri_and_version: str
    timestamp: str
    hostname: str
    app_name: str
    procid: str
    msgid: str
    structured_data: str
    msg: str
    timestamp2: str | None
    level: str | None
    thread: str | None
    clazz: str | None
    msg2: str | None


class SyslogHandler(DatagramProtocol):
    transport: asyncio.DatagramTransport

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        asyncio.ensure_future(self.handle_message(message))

    @staticmethod
    def alert_filter(msg: Message) -> bool:
        if msg.level:
            return "warn" in msg.level.lower() or "error" in msg.level.lower()
        else:
            return "warn" in msg.msg.lower() or "error" in msg.msg.lower()

    @staticmethod
    async def alert(msg: Message):
        """to override"""
        raise NotImplementedError()

    @staticmethod
    def info_filter(msg: Message) -> bool:
        if msg.level:
            return "info" in msg.level
        else:
            return "info" in msg.msg.lower()

    @staticmethod
    async def info(msg: Message):
        """to override"""
        raise NotImplementedError()

    async def handle_message(self, data: str):
        print(f"HANDLE {data}")

        s = data.split(" ")
        pri_and_version = s[0]
        timestamp = s[1]
        hostname = s[2]
        app_name = s[3]
        procid = s[4]
        msgid = s[5]
        structured_data = s[6]
        msg = " ".join(s[7:])

        message = Message(
            pri_and_version=pri_and_version,
            timestamp=timestamp,
            hostname=hostname,
            app_name=app_name,
            procid=procid,
            msgid=msgid,
            structured_data=structured_data,
            msg=msg,
            timestamp2=None,
            level=None,
            thread=None,
            clazz=None,
            msg2=None,
        )

        if "fabx-app" in app_name:
            s = msg.split(" ")

            try:
                # %white(%d{ISO8601}) %highlight(%-5level) [%blue(%t)]
                # %cyan(%c{1}): %msg%n%throwable
                timestamp2 = " ".join(s[0:1])
                level = s[2]
                thread = s[3]
                clazz = s[4]
                msg2 = s[5:]

                message = Message(
                    pri_and_version=pri_and_version,
                    timestamp=timestamp,
                    hostname=hostname,
                    app_name=app_name,
                    procid=procid,
                    msgid=msgid,
                    structured_data=structured_data,
                    msg=msg,
                    timestamp2=timestamp2,
                    level=level,
                    thread=thread,
                    clazz=clazz,
                    msg2="".join(msg2),
                )

                if self.alert_filter(message):
                    await self.alert(message)
                if self.info_filter(message):
                    await self.info(message)

            except IndexError:
                print(f"- unknown format - {msg}")
        else:
            if self.alert_filter(message):
                await self.alert(message)
            if self.info_filter(message):
                await self.info(message)
