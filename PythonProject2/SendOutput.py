import json
import requests
from Debugger import debug


class ServerOutput:
    def __init__(self, socket, info):
        self.socket = socket
        self.info = info

    def send_state(self, state: dict):
        msg = json.dumps(state).encode()
        self.socket.sendto(msg, (self.info.UDP_IP, self.info.UDP_PORT))

    def send_output(self, output):
        try:
            resp = requests.post(self.info.url_output, json=output, timeout=1)
        except Exception as e:
            debug(f"error {e}", "ERROR")
            pass
        try:
            self.send_state(output)
        except Exception as e:
            debug("unity error", "ERROR")
            debug(f"error {e}", "ERROR")