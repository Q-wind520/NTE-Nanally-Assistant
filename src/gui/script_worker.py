from PySide6.QtCore import QThread, Signal

from core.packages.menu import ScriptInfo


class ScriptWorker(QThread):
    started_signal = Signal(str)
    finished_signal = Signal()
    error_signal = Signal(str)

    def __init__(self, script_info: ScriptInfo, times: int | None) -> None:
        super().__init__()
        self.script_info = script_info
        self.times = times

    def run(self) -> None:
        try:
            self.started_signal.emit(self.script_info.name)
            if self.script_info.need_times_param:
                self.script_info.runner(self.times)
            else:
                self.script_info.runner()
            self.finished_signal.emit()
        except Exception as e:
            self.error_signal.emit(str(e))
