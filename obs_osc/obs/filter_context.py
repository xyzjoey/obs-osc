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
