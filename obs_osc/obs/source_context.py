import obspython as obs

from .filter_context import FilterContext


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
            self._obs_parent_scene = obs.obs_scene_from_source(self._obs_parent_scene_source)
            self._obs_scene_item = obs.obs_scene_sceneitem_from_source(self._obs_parent_scene, self._obs_source)

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
        # set_enabled is not controllable from obs ui, it is different from toggling visibility
        # use set_visible instead which is more transparent for user
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
