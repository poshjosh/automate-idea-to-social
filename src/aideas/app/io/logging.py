from pyu.io.logging import SecretsMaskingFilter
from ..env import is_production

class SecretsMaskingLogFilter(SecretsMaskingFilter):
    def __init__(self, patterns: list[str] = None):
        super().__init__(patterns if patterns else
                         ["(password|key|secret|token|jwt|hash|signature|credential|auth|certificate|connection)"])

    def redact(self, value: any) -> any:
        if is_production():
            return super().redact(value)
        return value