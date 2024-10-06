from ..obs import service as obs_service


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
        print(f"osc.routes.source_media_next - Missing source name in address (address={address})")
        return

    if len(args) < 1:
        print(f"osc.routes.source_media_next - Expected 1 arg but get 0")
        return

    source_name = tokens[0]
    enabled = True if args[0] > 0 else False

    obs_service.source_set_enabled(source_name, enabled)


@osc_route("/*/muted")
def source_set_muted(address, *args):
    tokens = address[1:].split("/")

    if len(tokens) < 2:
        print(f"osc.routes.source_set_muted - Missing source name in address (address={address})")
        return

    if len(args) < 1:
        print(f"osc.routes.source_set_muted - Expected 1 arg but get 0")
        return

    source_name = tokens[0]
    muted = True if args[0] > 0 else False

    obs_service.source_set_muted(source_name, muted)


@osc_route("/*/media_restart")
def source_media_restart(address, *args):
    tokens = address[1:].split("/")

    if len(tokens) < 2:
        print(f"osc.routes.source_media_restart - Missing source name in address (address={address})")
        return

    obs_service.source_media_restart(tokens[0])


@osc_route("/*/media_stop")
def source_media_stop(address, *args):
    tokens = address[1:].split("/")

    if len(tokens) < 2:
        print(f"osc.routes.source_media_stop - Missing source name in address (address={address})")
        return

    obs_service.source_media_stop(tokens[0])


@osc_route("/*/media_prev")
def source_media_prev(address, *args):
    tokens = address[1:].split("/")

    if len(tokens) < 2:
        print(f"osc.routes.source_media_prev - Missing source name in address (address={address})")
        return

    obs_service.source_media_prev(tokens[0])


@osc_route("/*/media_next")
def source_media_next(address, *args):
    tokens = address[1:].split("/")

    if len(tokens) < 2:
        print(f"osc.routes.source_media_next - Missing source name in address (address={address})")
        return

    obs_service.source_media_next(tokens[0])


@osc_route("/*/set_text")
def source_set_text(address, *args):
    tokens = address[1:].split("/")

    if len(tokens) < 2:
        print(f"osc.routes.source_set_text - Missing source name in address (address={address})")
        return

    if len(args) < 1:
        print(f"osc.routes.source_set_text - Expected 1 arg but get 0")
        return

    obs_service.source_set_text(tokens[0], args[0])


@osc_route("/*/filter/*/enabled")
def filter_set_enabled(address, *args):
    tokens = address[1:].split("/")

    if len(tokens) < 4:
        print(f"osc.routes.source_media_next - Missing source or filter name in address (address={address})")
        return

    if len(args) < 1:
        print(f"osc.routes.source_media_next - Expected 1 arg but get 0")
        return

    source_name = tokens[0]
    filter_name = tokens[2]
    enabled = True if args[0] > 0 else False

    obs_service.filter_set_enabled(source_name, filter_name, enabled)


@osc_route("/scene")
def set_scene(address, *args):
    if len(args) < 1:
        print(f"osc.routes.set_scene - Expected 1 arg but get 0")
        return

    obs_service.set_current_scene(args[0])
