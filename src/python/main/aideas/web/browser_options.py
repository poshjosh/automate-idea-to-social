import logging
import os

from selenium.webdriver.chrome.options import Options

from ..env import Env, get_path, get_value, require_path

logger = logging.getLogger(__name__)


def chrome_options(config: dict[str, any], agent_name: str) -> Options:
    chrome_config = config['browser']['chrome']

    option_args: list[str] = chrome_config.get('options', {}).get('args', [])
    use_profile: bool = chrome_config.get('use-profile', False)
    if use_profile:
        __add_options_from_env(option_args)

    preferences = {}
    preferences.update(chrome_config.get('prefs', {}))
    __add_prefs_from_env(preferences, agent_name)

    return __collect_options(option_args, preferences)


def __add_options_from_env(add_to: list[str]):
    env_opt_args: list[str] = [
        get_path(Env.BROWSER_CHROME_OPTIONS_USERDATA_DIR),
        get_value(Env.BROWSER_CHROME_OPTIONS_PROFILE_DIR)
    ]
    for env_opt_arg in env_opt_args:
        if not env_opt_arg:
            continue
        if env_opt_arg in add_to:
            add_to[add_to.index(env_opt_arg)] = env_opt_arg
        else:
            add_to.append(env_opt_arg)


def __add_prefs_from_env(add_to: dict[str, str], agent_name: str):
    output_dir = os.path.join(require_path(Env.OUTPUT_DIR), agent_name)
    if os.path.exists(output_dir) is False:
        os.makedirs(output_dir)
        logger.debug(f"Created dirs: {output_dir}")
    add_to.update({'download.default_directory': output_dir})


def __collect_options(option_args: list[str], prefs: dict[str, str]) -> Options:
    logger.debug(f'Will create browser with\nprefs: {prefs}\noptions: {option_args}')
    options = Options()
    if option_args is not None:
        for arg in option_args:
            if not arg:
                continue
            options.add_argument("--" + arg)

    if prefs is not None:
        options.add_experimental_option("prefs", prefs)
    return options
