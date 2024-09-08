from pythonosc.dispatcher import Dispatcher

from .routes import OscRoutes


class OscDispatcher(Dispatcher):
    def __init__(self, connection_info):
        super().__init__()
        self._info = connection_info

        for route_args in OscRoutes.routes:
            self.map(*route_args)

        self.set_default_handler(self._on_unknown_msg)

    def __repr__(self):
        return f"OscDispatcher(host={self._info.host}, port={self._info.port})"

    def _on_unknown_msg(self, address, *args):
        print(f"{self} - Unknown osc message (address={address}, args={args})")
