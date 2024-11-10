from pathlib import Path
from types import ModuleType
import importlib
import subprocess
import sys

import obspython as obs


class ScriptContext:
    obs_osc_module = None
    osc_server = None


class ScriptUtils:
    @classmethod
    def _recursive_reload_impl(cls, module, root_package_name, visited_modules):
        if not module.__package__.startswith(root_package_name):
            return
        if module in visited_modules:
            return

        visited_modules.add(module)

        for attr_name in dir(module):
            attr = getattr(module, attr_name)

            if type(attr) is ModuleType:
                dependant_module = attr
                cls._recursive_reload_impl(dependant_module, root_package_name, visited_modules)
            elif hasattr(attr, "__module__"):
                dependant_module = sys.modules[attr.__module__]
                cls._recursive_reload_impl(dependant_module, root_package_name, visited_modules)

        return importlib.reload(module)

    @classmethod
    def _recursive_reload(cls, module):
        visited_modules = set()
        return cls._recursive_reload_impl(module, module.__package__, visited_modules)

    @staticmethod
    def install_requirements():
        requirements_file_path = Path(__file__).parent.resolve() / "requirements.txt"
        print(f"Install requirements from `{requirements_file_path}`...")

        obs_config = obs.obs_frontend_get_global_config()
        python_dir = obs.config_get_string(obs_config, "Python", "Path64bit") or obs.config_get_string(obs_config, "Python", "Path32bit")

        if python_dir is None:
            print("Python path is not set in OBS Python Settings")
            return

        subprocess.check_call(
            [
                Path(python_dir) / "python",
                "-m",
                "pip",
                "install",
                "-r",
                requirements_file_path,
            ]
        )

    @classmethod
    def try_import_obs_osc(cls):
        try:
            import obs_osc

            return cls._recursive_reload(obs_osc)
        except ImportError:
            return None


def script_properties():
    props = obs.obs_properties_create()

    obs.obs_properties_add_text(props, "host", "Host IP", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_int(props, "listen_port", "Listen port", 1, 400000, 1)
    obs.obs_properties_add_bool(props, "enable", "Enable")
    obs.obs_properties_add_button(props, "install_requirements", "Install requirements", on_install_requirements_button)

    return props


def script_defaults(settings):
    obs.obs_data_set_default_string(settings, "host", "127.0.0.1")
    obs.obs_data_set_default_int(settings, "listen_port", 57120)
    obs.obs_data_set_default_bool(settings, "enable", False)


def script_load(settings):
    ScriptContext.obs_osc_module = ScriptUtils.try_import_obs_osc()


def script_update(settings):
    enable = obs.obs_data_get_bool(settings, "enable")

    if enable:
        if ScriptContext.obs_osc_module is None:
            print("Failed to import necessary modules. Please install requirements.")

        elif ScriptContext.osc_server is None:
            host = obs.obs_data_get_string(settings, "host")
            listen_port = obs.obs_data_get_int(settings, "listen_port")

            ScriptContext.osc_server = ScriptContext.obs_osc_module.OscServer(host, listen_port)
            ScriptContext.osc_server.start()

    elif ScriptContext.osc_server is not None:
        ScriptContext.osc_server.stop()
        ScriptContext.osc_server = None


def script_unload():
    if ScriptContext.osc_server is not None:
        ScriptContext.osc_server.stop()
        ScriptContext.osc_server = None


def on_install_requirements_button(props, button):
    if ScriptContext.obs_osc_module is not None:
        print("Requirements are already installed")
    else:
        ScriptUtils.install_requirements()
        ScriptContext.obs_osc_module = ScriptUtils.try_import_obs_osc()
        print("Installed requirements successfully. Please re-enable script.")
