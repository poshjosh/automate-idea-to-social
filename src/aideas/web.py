from flask import Flask, render_template, request
import logging.config
import os.path

from pyu.io.logging import SecretsMaskingFilter
from app.config_loader import ConfigLoader
from app.env import Env
from app.web_service import WebService, ValidationError

web_app = Flask(__name__)

web_servce = WebService()

secrets_masking_filter = SecretsMaskingFilter(
    ["(pass|key|secret|token|jwt|hash|signature|credential|auth|certificate|connection|pat)"])


@web_app.route('/')
def index():
    return render_template('index.html', **web_servce.index())


@web_app.route('/automate/index.html')
def automate():
    return render_template('automate/index.html', **web_servce.automate())


@web_app.route('/automate/details.html')
def automate_task():
    tag = request.args['tag']
    return render_template('automate/details.html', **web_servce.automate_task(tag))


@web_app.route('/automate/start', methods=['POST'])
def automate_start():
    try:
        result = web_servce.automate_start(request.form, request.files)
        result_str = (result.pretty_str("\n", "&emsp;")
                      .replace("ActionResult(", "(")
                      .replace(", Action(", ", (")
                      .replace("(success=True,", '(<span style="color:green">SUCCESS</span>,')
                      .replace("(success=False,", '(<span style="color:red">FAILURE</span>,'))
        result_str = secrets_masking_filter.redact(result_str)
        result_str = result_str.replace("\n", "<br>")  # Replace his only after masking secrets
        args = {"info": f'<span style="font-size:0.75rem;">{result_str}</span>'}
    except Exception as ex:
        default_err_msg = "An unexpected error occurred while trying to automate."
        if isinstance(ex, ValidationError):
            args = {"error": ex.message if ex.message else default_err_msg}
        else:
            args = {"error": default_err_msg}
    template_args = {**web_servce.automate(), **args}
    return render_template('automate/index.html', **template_args)


if __name__ == '__main__':

    Env.set_defaults()

    config_loader = ConfigLoader(os.path.join(os.getcwd(), 'resources', 'config'))

    logging.config.dictConfig(config_loader.load_logging_config())

    web_app.run(
        host='0.0.0.0',
        port=os.environ.get('APP_PORT', 5551),
        debug=os.environ.get('APP_DEBUG', True))
