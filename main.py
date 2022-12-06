import socketserver
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


class SyslogHandler(socketserver.BaseRequestHandler):  # , DatagramProtocol):
    # transport: DatagramTransport

    # def connection_made(self, transport):
    #     self.transport = transport
    #
    # def datagram_received(self, data, addr):
    #     message = data.decode()
    #     print(f'Received {message} from {addr}')
    #     self.handle_message(message)

    def handle(self):
        data = bytes.decode(self.request[0].strip(), encoding="utf-8")
        self.handle_message(data)

    @staticmethod
    def alert_filter(msg: Message) -> bool:
        if msg.level:
            return "warn" in msg.level or "error" in msg.level
        else:
            return "warn" in msg.msg.lower() or "error" in msg.msg.lower()

    @staticmethod
    def alert(msg: Message):
        print(f"ALERT {msg}")

    @staticmethod
    def info_filter(msg: Message) -> bool:
        if msg.level:
            return "info" in msg.level
        else:
            return "info" in msg.msg.lower()

    @staticmethod
    def info(msg: Message):
        print(f"INFO {msg}")

    def handle_message(self, data: str):
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
                    self.alert(message)
                if self.info_filter(message):
                    self.info(message)

            except IndexError:
                print(f"- unknown format - {msg}")
        else:
            if self.alert_filter(message):
                self.alert(message)
            if self.info_filter(message):
                self.info(message)


# if __name__ == "__main__":
#     HOST, PORT = "0.0.0.0", 12312
#
#     server = socketserver.UDPServer((HOST, PORT), SyslogHandler)
#
#     print(f"waiting for messages on {HOST}:{PORT}...")
#     server.serve_forever()
