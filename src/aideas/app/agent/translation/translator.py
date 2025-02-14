import logging
import os
from typing import Union

import requests

logger = logging.getLogger(__name__)

class TextLines:
    def __init__(self, text: str):
        if not text:
            raise ValueError("Text is required")
        self.__lines_without_breaks: [str] = []
        self.__breaks: [int] = []
        self.__len = 0
        for line in text.splitlines(False):
            line = line.strip()
            if line == '' or len(line) == 0:
                self.__breaks.append(self.__len)
            else:
                self.__lines_without_breaks.append(line)
            self.__len += 1

    def compose(self, lines: [str]) -> str:
        return '\n'.join(self.with_breaks(lines))

    def with_breaks(self, lines: [str]) -> [str]:
        result = [*lines]
        for break_idx in self.__breaks:
            result.insert(break_idx, "")
        return result

    def get_lines_without_breaks(self) -> [str]:
        return [e for e in self.__lines_without_breaks]

    def get_break_count(self) -> int:
        return len(self.__breaks)

    def __len__(self):
        return self.__len


class Translator:
    @classmethod
    def of_config(cls, agent_config: dict[str, any]) -> 'Translator':
        net_config = agent_config['net']
        return cls(net_config['service-url'],
                   net_config.get('chunk-size', 10000),
                   net_config.get('user-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'))

    __verbose = True

    def __init__(self,
                 service_url: str,
                 chunk_size: int = 10000,
                 user_agent: str = "aideas/translator"):
        self.__service_url = service_url
        self.__user_agent = user_agent
        self.__chunk_size = chunk_size
        # Do not put letters here, they may be translated or cause other inconsistencies.
        self.__separator: str = "~~~"

    @staticmethod
    def _chunkify(text_list: list[str], chunk_size: int) -> [str]:
        text_size = 0
        result_list = []
        chunk = []
        for line in text_list:
            line = line.strip()
            if text_size + len(line) < chunk_size:
                chunk.append(line)
                text_size += len(line)
            elif chunk and len(line) < chunk_size:
                result_list.append(chunk)
                chunk = [line]
                text_size = len(line)
        result_list.append(chunk)
        return result_list

    def translate(self, text: Union[list[str], str], from_lang: str, to_lang: str) -> Union[list[str], str]:
        if isinstance(text, str):
            text_lines = TextLines(text)
            text_list = text_lines.get_lines_without_breaks()
        else:
            text_lines = None
            text_list = text

        chunks = Translator._chunkify(text_list, self.__chunk_size)

        result_big_list = []
        for chunk in chunks:
            if not chunk:
                continue
            result = self.__translate(chunk, from_lang, to_lang)
            result_big_list.extend(result)

        return text_lines.compose(result_big_list) if text_lines else result_big_list

    def translate_file_path(self, filepath: str, from_lang: str, to_lang: str):
        name, ext = os.path.splitext(os.path.basename(filepath))
        name_translated: str = self.translate(name, from_lang, to_lang)
        if name_translated and name_translated != name:
            return os.path.join(os.path.dirname(filepath), f'{name_translated}{ext}')
        parts: [str] = filepath.rsplit('.', 1)
        if len(parts) < 2:
            return filepath + "." + to_lang
        else:
            return parts[0] + "." + to_lang + "." + parts[1]

    def __translate(self,
                    text_list: list[str],
                    from_lang: str,
                    to_lang: str) -> list[str]:
        if self.__verbose:
            logger.debug(f"Translate new chunk with {sum(len(i) for i in text_list)} chars")
        text = f" {self.__separator} ".join(text_list)
        params = {"client": "gtx", "sl": from_lang, "tl": to_lang, "dt": "t", "q": text}
        headers = {
            "User-Agent": self.__user_agent
        }
        json_result = self.call_translation_service(params=params, headers=headers)
        return self._handle_result(json_result)

    def _handle_result(self, json_result) -> list[str]:
        if not json_result or not json_result[0]:
            return []

        result = []
        return_string = " ".join(i[0].strip() for i in json_result[0])
        split = return_string.split(self.__separator)
        split = map(lambda x: x.strip(), split)
        result.extend(split)
        return list(filter(lambda x: x, result))

    def call_translation_service(self, params: dict, headers: dict) -> list[str]:
        logger.debug(f"Requesting translation from: {self.__service_url}")
        r = requests.get(self.__service_url, params=params, headers=headers)
        return r.json()

    def get_separator(self) -> str:
        return self.__separator