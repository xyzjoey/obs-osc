import obspython as obs


class SceneControl:
    @classmethod
    def set_current_scene(cls, source_context):
        obs.obs_frontend_set_current_scene(source_context.obs_source)
