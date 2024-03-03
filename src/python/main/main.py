import os.path

from aideas.app import App

if __name__ == "__main__":
    App.of_defaults(os.path.join('aideas', 'config')).run()
