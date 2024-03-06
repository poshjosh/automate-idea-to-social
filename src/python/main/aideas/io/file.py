import logging
import os
import zipfile

logger = logging.getLogger(__name__)


def extract_zip_file(zip_file: str,
                     extract_to: str = os.getcwd(),
                     delete_zip_file: bool = False) -> bool:
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(extract_to)

            if delete_zip_file:
                try:
                    os.remove(zip_file)
                except Exception as ex:
                    logger.warning(f'Error deleting file: {zip_file}. {ex}')
        return True
    except Exception as ex:
        logger.error(f'Error extracting file: {zip_file}. {ex}')
        return False
