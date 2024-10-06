from .source_context import SourceContext
from .scene_control import SceneControl


def filter_set_enabled(source_name, filter_name, enabled):
    with SourceContext.find_source_by_name(source_name) as source_context:
        if source_context is None:
            print(f"obs.service.filter_set_enabled - Cannot find source (source_name={source_name})")
            return

        with source_context.find_filter_by_name(filter_name) as filter_context:
            if filter_context is None:
                print(f"obs.service.filter_set_enabled - Cannot find filter (filter_name={filter_name})")
                return

            filter_context.set_enabled(enabled)


def source_set_enabled(source_name, enabled):
    with SourceContext.find_source_by_name(source_name) as source_context:
        if source_context is None:
            print(f"obs.service.source_set_enabled - Cannot find source (source_name={source_name})")
            return

        source_context.set_enabled(enabled)


def source_set_muted(source_name, muted):
    with SourceContext.find_source_by_name(source_name) as source_context:
        if source_context is None:
            print(f"obs.service.source_set_muted - Cannot find source (source_name={source_name})")
            return

        source_context.set_muted(muted)


def source_media_restart(source_name):
    with SourceContext.find_source_by_name(source_name) as source_context:
        if source_context is None:
            print(f"obs.service.source_media_restart - Cannot find source (source_name={source_name})")
            return

        source_context.media_restart()


def source_media_stop(source_name):
    with SourceContext.find_source_by_name(source_name) as source_context:
        if source_context is None:
            print(f"obs.service.source_media_stop - Cannot find source (source_name={source_name})")
            return

        source_context.media_stop()


def source_media_prev(source_name):
    with SourceContext.find_source_by_name(source_name) as source_context:
        if source_context is None:
            print(f"obs.service.source_media_prev - Cannot find source (source_name={source_name})")
            return

        source_context.media_prev()


def source_media_next(source_name):
    with SourceContext.find_source_by_name(source_name) as source_context:
        if source_context is None:
            print(f"obs.service.source_media_next - Cannot find source (source_name={source_name})")
            return

        source_context.media_next()


def source_set_text(source_name, text):
    with SourceContext.find_source_by_name(source_name) as source_context:
        if source_context is None:
            print(f"obs.service.source_set_text - Cannot find source (source_name={source_name})")
            return

        source_context.set_text(text)


def set_current_scene(scene_name):
    with SourceContext.find_source_by_name(scene_name) as source_context:
        if source_context is None:
            print(f"obs.service.set_current_scene - Cannot find scene (scene_name={scene_name})")
            return

        if not source_context.is_scene():
            print(f"obs.service.set_current_scene - Not a scene (scene_name={scene_name})")
            return

        SceneControl.set_current_scene(source_context)
