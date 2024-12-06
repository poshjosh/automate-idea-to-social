from flask import Flask, render_template, request
import logging.config
import os.path

from app.app import App, AppArg
from app.config_loader import ConfigLoader
from app.env import Env

app = Flask(__name__)

APP_NAME = 'Aideas'
APP_TITLE = f'{APP_NAME} | Automate posting your ideas to social'


@app.route('/')
def index():
    return render_template('index.html', title=APP_TITLE, heading=APP_TITLE)


@app.route('/automate')
def automate():
    return render_template('automate.html', name=APP_NAME, title=APP_TITLE,
                           heading="Enter details of post to automatically send")


@app.route('/automate/start', methods=['POST'])
def automate_start():
    agents_key = AppArg.AGENTS.env_name.value.lower()
    agents = request.form.getlist(agents_key)
    return App.of_defaults(config_loader).run(agents).pretty_str("<br/>")


if __name__ == '__main__':

    Env.set_defaults()

    config_loader = ConfigLoader(os.path.join(os.getcwd(), 'resources', 'config'))

    logging.config.dictConfig(config_loader.load_logging_config())

    app.run(
        host='0.0.0.0',
        port=os.environ.get('APP_PORT', 5551),
        debug=os.environ.get('APP_DEBUG', True))
