import os


class Paths:
    @staticmethod
    def get_path(value: any, extra: str = None, default: any = None) -> any:
        if not value:
            return default
        path = Paths.__explicit(value)
        return path if not extra else os.path.join(path, extra)

    @staticmethod
    def require_path(value: any):
        path = Paths.__explicit(value)
        if not os.path.exists(path):
            raise FileNotFoundError(f'File not found: {path}')
        return path

    @staticmethod
    def __explicit(path: str) -> str:
        explicit: bool = path.startswith('/') or path.startswith('.')
        return path if explicit else os.path.join(os.getcwd(), path)
