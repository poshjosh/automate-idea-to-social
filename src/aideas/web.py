from flask import Flask, render_template, request
import logging.config
import os.path

from app.app import App
from app.config import AppConfig
from app.config_loader import ConfigLoader
from app.env import Env

web_app = Flask(__name__)

CONFIG_PATH = os.path.join(os.getcwd(), 'resources', 'config')

Env.set_defaults()

logging.config.dictConfig(ConfigLoader(CONFIG_PATH).load_logging_config())

app = AppConfig(ConfigLoader(CONFIG_PATH).load_app_config())


@web_app.route('/')
def index():
    return render_template('index.html', title=app.get_title(), heading=app.get_title())


@web_app.route('/automate')
def automate():
    return render_template('automate.html', title=app.get_title(),
                           heading="Enter details of post to automatically send")


@web_app.route('/automate/start', methods=['POST'])
def automate_start():
    config_loader = ConfigLoader(os.path.join(os.getcwd(), 'resources', 'config'), request.form)
    return App.of_defaults(config_loader).run(request.form).pretty_str("<br/>", "&emsp;")


if __name__ == '__main__':
    web_app.run(
        host='0.0.0.0',
        port=os.environ.get('APP_PORT', 5551),
        debug=os.environ.get('APP_DEBUG', True))
