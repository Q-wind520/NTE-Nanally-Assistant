import logging
from PySide6.QtCore import QObject, Signal


class _LogSignal(QObject):
    message = Signal(str)


_log_signal = _LogSignal()


class QtLogHandler(logging.Handler):
    """将 logging 输出桥接到 Qt signal，线程安全。"""

    def __init__(self, level: int = logging.INFO) -> None:
        super().__init__(level)
        self.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))

    def emit(self, record: logging.LogRecord) -> None:
        _log_signal.message.emit(self.format(record))


class QtStreamRedirector(QObject):
    """将 sys.stdout 输出桥接到 Qt signal，线程安全。"""

    new_text = Signal(str)

    def __init__(self) -> None:
        super().__init__()

    def write(self, text: str) -> None:
        if text:
            self.new_text.emit(text)

    def flush(self) -> None:
        pass


def get_log_signal() -> _LogSignal:
    return _log_signal
