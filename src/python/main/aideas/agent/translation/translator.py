import logging
import requests

logger = logging.getLogger(__name__)


class Translator:
    __verbose = True
    __default_user_agent = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                            "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

    def __init__(self,
                 service_url: str,
                 chunk_size: int = 10000,
                 user_agent: str = __default_user_agent):
        self.__service_url = service_url
        self.__user_agent = user_agent
        self.__chunk_size = chunk_size
        self.__separator: str = "u~~~u"

    def translate(self, text_list: list[str], from_lang: str, to_lang: str) -> list[str]:
        text_size = 0
        result_list = []
        chunk = []
        for line in text_list:
            line = line.strip()
            if text_size + len(line) < self.__chunk_size:
                chunk.append(line)
                text_size += len(line)
            elif chunk and len(line) < self.__chunk_size:
                result_list.append(chunk)
                chunk = [line]
                text_size = len(line)
        result_list.append(chunk)
        result_big_list = []
        for part in result_list:
            if part:
                if self.__verbose:
                    chars = sum(len(i) for i in part)
                    logger.debug(f"Translate new chunk with {chars} chars")
                result = self.__translate(part, from_lang, to_lang)
                result_big_list.extend(result)
        return result_big_list

    def __translate(self,
                    text_list: list[str],
                    from_lang: str,
                    to_lang: str) -> list[str]:
        text = f" {self.__separator} ".join(text_list)
        params = {"client": "gtx", "sl": from_lang, "tl": to_lang, "dt": "t", "q": text}
        headers = {
            "User-Agent": self.__user_agent
        }
        return self.call_translation_service(params=params, headers=headers)

    def call_translation_service(self, params: dict, headers: dict) -> list[str]:
        r = requests.get(self.__service_url, params=params, headers=headers)
        result = []
        try:
            json_result = r.json()
        except Exception as ex:
            logger.warning(f"{ex}")
        else:
            if json_result and json_result[0]:
                return_string = " ".join(i[0].strip() for i in json_result[0])
                split = return_string.split(self.__separator)
                split = map(lambda x: x.strip(), split)
                result.extend(split)
                result = list(filter(lambda x: x, result))
        return result

    def get_separator(self) -> str:
        return self.__separator
