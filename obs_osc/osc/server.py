from typing import NamedTuple
from threading import Thread

from pythonosc.osc_server import BlockingOSCUDPServer

from .dispatcher import OscDispatcher


class ConnectionInfo(NamedTuple):
    host: str
    port: int


class OscServer:
    def __init__(self, host, port):
        self._info = ConnectionInfo(host, port)
        self._dispatcher = OscDispatcher(self._info)
        self._server = BlockingOSCUDPServer((host, port), self._dispatcher)

        self._thread = None

    def __repr__(self):
        return f"OscServer(host={self._info.host}, port={self._info.port})"

    def start(self):
        print(f"{self} - Start")

        self._thread = Thread(target=self.serve_thread, daemon=True)
        self._thread.start()

    def stop(self):
        print(f"{self} - Stopping...", flush=True)

        self._server.shutdown()
        self._thread.join()
        self._server.server_close()

        print(f"{self} - Stopped")

    def serve_thread(self):
        self._server.serve_forever()
