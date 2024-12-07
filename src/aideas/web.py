from flask import Flask, render_template, request
import logging.config
import os.path

from app.config_loader import ConfigLoader
from app.env import Env
from app.web_service import WebService, ValidationError

web_app = Flask(__name__)

web_servce = WebService()


@web_app.route('/')
def index():
    return render_template('index.html', **web_servce.index())


@web_app.route('/automate')
def automate():
    return render_template('automate.html', **web_servce.automate())


@web_app.route('/automate/start', methods=['POST'])
def automate_start():
    try:
        result_str = web_servce.automate_start(
            request.form, request.files).pretty_str("<br/>", "&emsp;")
        args = {"info": result_str}
    except Exception as ex:
        default_err_msg = "An unexpected error occurred while trying to automate."
        if isinstance(ex, ValidationError):
            args = {"error": ex.message if ex.message else default_err_msg}
        else:
            args = {"error": default_err_msg}
    template_args = {**web_servce.automate(), **args}
    return render_template('automate.html', **template_args)


if __name__ == '__main__':

    Env.set_defaults()

    config_loader = ConfigLoader(os.path.join(os.getcwd(), 'resources', 'config'))

    logging.config.dictConfig(config_loader.load_logging_config())

    web_app.run(
        host='0.0.0.0',
        port=os.environ.get('APP_PORT', 5551),
        debug=os.environ.get('APP_DEBUG', True))
