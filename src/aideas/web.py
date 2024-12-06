from flask import Flask, render_template, request
import logging.config
import os.path

from app.app import App, AppArg
from app.config_loader import ConfigLoader
from app.env import Env

web_app = Flask(__name__)

Env.set_defaults()

config_loader = ConfigLoader(os.path.join(os.getcwd(), 'resources', 'config'))

logging.config.dictConfig(config_loader.load_logging_config())

app = App.of_defaults(config_loader)


@web_app.route('/')
def index():
    return render_template('index.html', title=app.title, heading=app.title)


@web_app.route('/automate')
def automate():
    return render_template('automate.html', title=app.title,
                           heading="Enter details of post to automatically send")


@web_app.route('/automate/start', methods=['POST'])
def automate_start():
    agents = request.form.getlist(AppArg.AGENTS.env_name.value.lower())
    return app.run(agents).pretty_str("<br/>", "&emsp;")


if __name__ == '__main__':
    web_app.run(
        host='0.0.0.0',
        port=os.environ.get('APP_PORT', 5551),
        debug=os.environ.get('APP_DEBUG', True))
