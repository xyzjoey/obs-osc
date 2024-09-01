# move to obs_osc/obs/source_context.py
import obspython as obs


class FilterContext:
    def __init__(self, obs_filter):
        self._obs_filter = obs_filter

    def __enter__(self):
        if self._obs_filter is not None:
            return self
        else:
            return None

    def __exit__(self, *_):
        if self._obs_filter is not None:
            obs.obs_source_release(self._obs_filter)

    def set_enabled(self, enabled):
        obs.obs_source_set_enabled(self._obs_filter, enabled)


class SourceContext:
    def __init__(self, obs_source):
        self.name = None

        self._obs_source = obs_source
        self._obs_parent_scene_source = None
        self._obs_parent_scene = None
        self._obs_scene_item = None

        if self._obs_source is not None:
            self.name = obs.obs_source_get_name(self._obs_source)

            self._obs_parent_scene_source = obs.obs_frontend_get_current_scene()
            self._obs_parent_scene = obs.obs_scene_from_source(
                self._obs_parent_scene_source
            )
            self._obs_scene_item = obs.obs_scene_sceneitem_from_source(
                self._obs_parent_scene, self._obs_source
            )

    def __repr__(self):
        return f"SourceContext(name={self.name})"

    def __enter__(self):
        if self._obs_source is not None:
            return self
        else:
            return None

    def __exit__(self, *_):
        if self._obs_source is not None:
            obs.obs_source_release(self._obs_source)
            obs.obs_source_release(self._obs_parent_scene_source)

            if self._obs_scene_item is not None:
                obs.obs_sceneitem_release(self._obs_scene_item)

    @classmethod
    def find_source_by_name(cls, source_name):
        obs_source = obs.obs_get_source_by_name(source_name)
        return cls(obs_source)

    def find_filter_by_name(self, filter_name):
        obs_filter = obs.obs_source_get_filter_by_name(self._obs_source, filter_name)
        return FilterContext(obs_filter)

    def set_enabled(self, enabled):
        # set_enabled is not controllable from obs ui, does not toggle visibility icon
        # use set_visible instead which is more intuitive for user
        # obs.obs_source_set_enabled(self._obs_source, enabled)

        if self._obs_scene_item is not None:
            obs.obs_sceneitem_set_visible(self._obs_scene_item, enabled)
        else:
            print(f"{self} - Not allowed to enable/disable non scene item")

    def set_muted(self, muted):
        obs.obs_source_set_muted(self._obs_source, muted)

    def media_restart(self):
        obs.obs_source_media_restart(self._obs_source)

    def media_stop(self):
        obs.obs_source_media_stop(self._obs_source)

    def media_prev(self):
        obs.obs_source_media_previous(self._obs_source)

    def media_next(self):
        obs.obs_source_media_next(self._obs_source)

    def set_text(self, text):
        obs_data = obs.obs_source_get_settings(self._obs_source)
        obs.obs_data_set_string(obs_data, "text", text)
        obs.obs_source_update(self._obs_source, obs_data)
        obs.obs_data_release(obs_data)


class SceneContext:
    def __init__(self, obs_source):
        pass


# move to obs_osc/obs/service.py
class obs_service:
    @staticmethod
    def filter_set_enabled(source_name, filter_name, enabled):
        with SourceContext.find_source_by_name(source_name) as source_context:
            if source_context is None:
                print(
                    f"obs.service.filter_set_enabled - Cannot find source (source_name={source_name})"
                )
                return

            with source_context.find_filter_by_name(filter_name) as filter_context:
                if filter_context is None:
                    print(
                        f"obs.service.filter_set_enabled - Cannot find filter (filter_name={filter_name})"
                    )
                    return

                filter_context.set_enabled(enabled)

    @staticmethod
    def source_set_enabled(source_name, enabled):
        with SourceContext.find_source_by_name(source_name) as source_context:
            if source_context is None:
                print(
                    f"obs.service.source_set_enabled - Cannot find source (source_name={source_name})"
                )
                return

            source_context.set_enabled(enabled)

    @staticmethod
    def source_set_muted(source_name, muted):
        with SourceContext.find_source_by_name(source_name) as source_context:
            if source_context is None:
                print(
                    f"obs.service.source_set_muted - Cannot find source (source_name={source_name})"
                )
                return

            source_context.set_muted(muted)

    @staticmethod
    def source_media_restart(source_name):
        with SourceContext.find_source_by_name(source_name) as source_context:
            if source_context is None:
                print(
                    f"obs.service.source_media_restart - Cannot find source (source_name={source_name})"
                )
                return

            source_context.media_restart()

    @staticmethod
    def source_media_stop(source_name):
        with SourceContext.find_source_by_name(source_name) as source_context:
            if source_context is None:
                print(
                    f"obs.service.source_media_stop - Cannot find source (source_name={source_name})"
                )
                return

            source_context.media_stop()

    @staticmethod
    def source_media_prev(source_name):
        with SourceContext.find_source_by_name(source_name) as source_context:
            if source_context is None:
                print(
                    f"obs.service.source_media_prev - Cannot find source (source_name={source_name})"
                )
                return

            source_context.media_prev()

    @staticmethod
    def source_media_next(source_name):
        with SourceContext.find_source_by_name(source_name) as source_context:
            if source_context is None:
                print(
                    f"obs.service.source_media_next - Cannot find source (source_name={source_name})"
                )
                return

            source_context.media_next()

    @staticmethod
    def source_set_text(source_name, text):
        with SourceContext.find_source_by_name(source_name) as source_context:
            if source_context is None:
                print(
                    f"obs.service.source_set_text - Cannot find source (source_name={source_name})"
                )
                return

            source_context.set_text(text)


# move to obs_osc/osc/routes.py
class OscRoutes:
    routes = []


def osc_route(address_pattern, *args):
    def registered_func(func):
        OscRoutes.routes.append((address_pattern, func, *args))
        return func

    return registered_func


@osc_route("/*/enabled")
def source_set_enabled(address, *args):
    tokens = address[1:].split("/")

    if len(tokens) < 2:
        print(
            f"osc.routes.source_media_next - Missing source name in address (address={address})"
        )
        return

    if len(args) < 1:
        print(f"osc.routes.source_media_next - Missing arg")
        return

    source_name = tokens[0]
    enabled = True if args[0] > 0 else False

    obs_service.source_set_enabled(source_name, enabled)


@osc_route("/*/muted")
def source_set_muted(address, *args):
    tokens = address[1:].split("/")

    if len(tokens) < 2:
        print(
            f"osc.routes.source_set_muted - Missing source name in address (address={address})"
        )
        return

    if len(args) < 1:
        print(f"osc.routes.source_set_muted - Missing arg")
        return

    source_name = tokens[0]
    muted = True if args[0] > 0 else False

    obs_service.source_set_muted(source_name, muted)


@osc_route("/*/media_restart")
def source_media_restart(address, *args):
    tokens = address[1:].split("/")

    if len(tokens) < 2:
        print(
            f"osc.routes.source_media_restart - Missing source name in address (address={address})"
        )
        return

    obs_service.source_media_restart(tokens[0])


@osc_route("/*/media_stop")
def source_media_stop(address, *args):
    tokens = address[1:].split("/")

    if len(tokens) < 2:
        print(
            f"osc.routes.source_media_stop - Missing source name in address (address={address})"
        )
        return

    obs_service.source_media_stop(tokens[0])


@osc_route("/*/media_prev")
def source_media_prev(address, *args):
    tokens = address[1:].split("/")

    if len(tokens) < 2:
        print(
            f"osc.routes.source_media_prev - Missing source name in address (address={address})"
        )
        return

    obs_service.source_media_prev(tokens[0])


@osc_route("/*/media_next")
def source_media_next(address, *args):
    tokens = address[1:].split("/")

    if len(tokens) < 2:
        print(
            f"osc.routes.source_media_next - Missing source name in address (address={address})"
        )
        return

    obs_service.source_media_next(tokens[0])


@osc_route("/*/set_text")
def source_set_text(address, *args):
    tokens = address[1:].split("/")

    if len(tokens) < 2:
        print(
            f"osc.routes.source_set_text - Missing source name in address (address={address})"
        )
        return

    if len(args) < 1:
        print(f"osc.routes.source_set_text - Missing text to set in args")
        return

    obs_service.source_set_text(tokens[0], args[0])


@osc_route("/*/filter/*/enabled")
def filter_set_enabled(address, *args):
    tokens = address[1:].split("/")

    if len(tokens) < 4:
        print(
            f"osc.routes.source_media_next - Missing source or filter name in address (address={address})"
        )
        return

    if len(args) < 1:
        print(f"osc.routes.source_media_next - Missing arg (args={args})")
        return

    source_name = tokens[0]
    filter_name = tokens[2]
    enabled = True if args[0] > 0 else False

    obs_service.filter_set_enabled(source_name, filter_name, enabled)


# move to obs_osc/osc/server.py
from typing import NamedTuple
from threading import Thread

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

# import obspython as obs


class ConnectionInfo(NamedTuple):
    host: str
    port: int


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
        print(
            f"{self} - Unknown osc message (address={address}, args={args})", flush=True
        )


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
        print(f"{self} - Stopping...")

        self._server.shutdown()
        self._thread.join()
        self._server.server_close()

        print(f"{self} - Stopped")

    def serve_thread(self):
        self._server.serve_forever()


# osc_script.py
# import obspython as obs


class ScriptContext:
    osc_server = None


def script_properties():
    props = obs.obs_properties_create()

    obs.obs_properties_add_text(props, "host", "Host IP", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_int(props, "listen_port", "Listen port", 1, 400000, 1)

    return props


def script_defaults(settings):
    obs.obs_data_set_default_string(settings, "host", "127.0.0.1")
    obs.obs_data_set_default_int(settings, "listen_port", 57120)


def script_load(settings):

    host = obs.obs_data_get_string(settings, "host")
    listen_port = obs.obs_data_get_int(settings, "listen_port")

    ScriptContext.osc_server = OscServer(host, listen_port)
    ScriptContext.osc_server.start()


def script_unload():
    if ScriptContext.osc_server is not None:
        ScriptContext.osc_server.stop()
        ScriptContext.osc_server = None
