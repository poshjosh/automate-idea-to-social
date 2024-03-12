import os.path

from aideas.app import App, ARG_AGENTS, get_list_arg


if __name__ == "__main__":
    agents: [str] = get_list_arg(ARG_AGENTS)
    App.of_defaults(os.path.join('aideas', 'config')).run(agents)

