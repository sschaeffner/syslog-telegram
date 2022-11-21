import socketserver


def alert(msg: str):
    print(f"ALERT {msg}")


def handle_message(data: str):
    print(f"HANDLE {data}")

    # <14>1 2022-11-14T21:11:02Z 2f7c516ee87b fabx-app-1 6573 - -
    # <14>1 2022-11-14T21:11:26Z 2f7c516ee87b fabx-app-1 6573 - -
    # ^^^^ PRI -> Priority
    #     ^ VERSION -> 1 for RFC5424
    #       ^^^^^^^^^^^^^^^^^^^^ TIMESTAMP according to RFC3339
    #                            ^^^^^^^^^^^^ HOSTNAME (container name)
    #                                         ^^^^^^^^^^ APP-NAME
    #                                                    ^^^^ PROCID
    #                                                         ^ MSGID
    #                                                           ^
    s = data.split(" ")
    pri_and_version = s[0]
    timestamp = s[1]
    hostname = s[2]
    app_name = s[3]
    procid = s[4]
    msgid = s[5]
    structured_data = s[6]
    msg = " ".join(s[7:])

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

            if "warn" in level or "error" in level:
                alert(msg)

            return

        except IndexError:
            print(f"- unknown format - {msg}")

    if ("warn" in msg.lower() or
            "error" in msg.lower()):
        alert(msg)


class SyslogHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = bytes.decode(self.request[0].strip(), encoding="utf-8")
        handle_message(data)


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 12312

    server = socketserver.UDPServer((HOST, PORT), SyslogHandler)

    print(f"waiting for messages on {HOST}:{PORT}...")
    server.serve_forever()
