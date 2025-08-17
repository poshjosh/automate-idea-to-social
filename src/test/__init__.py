import os

from aideas.app.app import App
from aideas.app.config_loader import CONFIG_DIR

App.init(os.path.join(os.getcwd(), 'test', CONFIG_DIR))
