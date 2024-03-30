import logging
import requests

logger = logging.getLogger(__name__)


def download_file(url: str, save_to: str) -> bool:
    try:
        response = requests.get(url)
    except OSError:
        logger.warning(f'No connection to the server! URL: {url}')
        return False

    logger.debug(f'Status {response.status_code}, URL: {url}')
    if response.status_code == 200:
        open(save_to, 'wb').write(response.content)
        return True
    else:
        logger.debug('Request not successful!.')
        return False
