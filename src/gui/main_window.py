from __future__ import annotations

import logging
import os
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QFont, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QPushButton,
    QSpinBox,
    QStatusBar,
    QSystemTrayIcon,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QMessageBox,
)

from core.packages.constants import DEFAULT_PROCESS_NAME, DEFAULT_TITLE, DEFAULT_VERSION
from core.packages.process import is_process_running
from core.packages.window import get_hwnd, get_window, WindowNotFoundError, WindowInvalidError
from core.packages.menu import _register_builtin_scripts, get_registry

from gui.script_worker import ScriptWorker
from gui.log_handler import get_log_signal

logger = logging.getLogger(__name__)


def _icon_path() -> str:
    candidates = [
        "docs/img/icon.ico",
        "docs/img/icon.png",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return ""


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{DEFAULT_TITLE} v{DEFAULT_VERSION}")
        self.resize(960, 540)

        icon = _icon_path()
        if icon:
            self.setWindowIcon(QIcon(icon))

        self._worker: ScriptWorker | None = None

        self._build_ui()
        self._setup_tray()
        self._connect_signals()
        self._populate_scripts()
        self._start_status_poll()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(8)

        # --- 游戏状态 ---
        status_group = QGroupBox("游戏状态")
        status_layout = QHBoxLayout(status_group)
        self._process_label = QLabel("等待检测...")
        self._resolution_label = QLabel("等待检测...")
        status_layout.addWidget(self._process_label)
        status_layout.addWidget(self._resolution_label)
        status_layout.addStretch()
        root.addWidget(status_group)

        # --- 脚本控制 ---
        control_group = QGroupBox("脚本控制")
        control_layout = QHBoxLayout(control_group)

        control_layout.addWidget(QLabel("脚本:"))
        self._script_combo = QComboBox()
        self._script_combo.setMinimumWidth(200)
        control_layout.addWidget(self._script_combo)

        control_layout.addWidget(QLabel("执行次数:"))
        self._times_spin = QSpinBox()
        self._times_spin.setRange(1, 9999)
        self._times_spin.setValue(1)
        control_layout.addWidget(self._times_spin)

        self._start_btn = QPushButton("▶ 开始执行")
        self._stop_btn = QPushButton("■ 停止")
        self._stop_btn.setEnabled(False)
        self._clear_btn = QPushButton("清空日志")

        control_layout.addWidget(self._start_btn)
        control_layout.addWidget(self._stop_btn)
        control_layout.addWidget(self._clear_btn)
        control_layout.addStretch()
        root.addWidget(control_group)

        # --- 日志输出 ---
        self._log_output = QTextEdit()
        self._log_output.setReadOnly(True)
        self._log_output.setFont(QFont("Consolas", 10))
        self._log_output.document().setMaximumBlockCount(5000)
        root.addWidget(self._log_output)

        # --- 菜单栏 ---
        menubar = self.menuBar()
        file_menu = menubar.addMenu("文件(&F)")
        exit_action = QAction("退出(&X)", self)
        exit_action.triggered.connect(self._quit_app)
        file_menu.addAction(exit_action)

        # --- 状态栏 ---
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage("就绪")

    # ------------------------------------------------------------------
    # 脚本列表
    # ------------------------------------------------------------------

    def _populate_scripts(self) -> None:
        _register_builtin_scripts()
        all_scripts = get_registry().get_all()
        self._script_combo.clear()
        for key, info in all_scripts.items():
            if key == "0":
                continue
            self._script_combo.addItem(f"{info.name}  -  {info.description}", info)
        self._on_script_changed(0)

    # ------------------------------------------------------------------
    # 信号连接
    # ------------------------------------------------------------------

    def _connect_signals(self) -> None:
        self._script_combo.currentIndexChanged.connect(self._on_script_changed)
        self._start_btn.clicked.connect(self._start_script)
        self._stop_btn.clicked.connect(self._stop_script)
        self._clear_btn.clicked.connect(self._log_output.clear)
        get_log_signal().message.connect(self._append_log)

    # ------------------------------------------------------------------
    # 脚本启停
    # ------------------------------------------------------------------

    def _on_script_changed(self, _index: int) -> None:
        info = self._script_combo.currentData()
        if info is not None:
            self._times_spin.setEnabled(info.need_times_param)

    def _start_script(self) -> None:
        info = self._script_combo.currentData()
        if info is None:
            self._append_log("[WARN] 没有可用的脚本")
            return

        if self._worker is not None and self._worker.isRunning():
            self._append_log("[WARN] 已有脚本正在运行，请先停止")
            return

        times = self._times_spin.value() if info.need_times_param else None
        self._worker = ScriptWorker(info, times)
        self._worker.started_signal.connect(self._on_worker_started)
        self._worker.finished_signal.connect(self._on_worker_finished)
        self._worker.error_signal.connect(self._on_worker_error)
        self._worker.finished.connect(self._on_worker_done)
        self._worker.start()

    def _stop_script(self) -> None:
        if self._worker is None or not self._worker.isRunning():
            return
        self._append_log("[WARN] 正在强制终止脚本...")
        self._worker.finished.disconnect(self._on_worker_done)
        self._worker.terminate()
        self._worker.wait(3000)
        self._on_worker_done()

    # --- worker callbacks ---

    def _on_worker_started(self, name: str) -> None:
        self._start_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
        self._script_combo.setEnabled(False)
        self._status_bar.showMessage(f"运行中: {name}")

    def _on_worker_finished(self) -> None:
        self._append_log("[INFO] 脚本执行完成")

    def _on_worker_error(self, msg: str) -> None:
        self._append_log(f"[ERROR] 脚本异常: {msg}")

    def _on_worker_done(self) -> None:
        self._start_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        self._script_combo.setEnabled(True)
        self._status_bar.showMessage("就绪")

    # ------------------------------------------------------------------
    # 日志
    # ------------------------------------------------------------------

    def _append_log(self, text: str) -> None:
        self._log_output.append(text.rstrip("\n"))

    # ------------------------------------------------------------------
    # 状态轮询
    # ------------------------------------------------------------------

    def _start_status_poll(self) -> None:
        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._poll_status)
        self._poll_timer.start(2000)
        self._poll_status()

    def _poll_status(self) -> None:
        # 进程
        try:
            running = is_process_running(DEFAULT_PROCESS_NAME)
        except Exception:
            running = False
        if running:
            self._process_label.setText(f"进程: ● {DEFAULT_PROCESS_NAME} 运行中")
            self._process_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self._process_label.setText(f"进程: ● {DEFAULT_PROCESS_NAME} 未检测到")
            self._process_label.setStyleSheet("color: red; font-weight: bold;")

        # 分辨率
        try:
            hwnd = get_hwnd(DEFAULT_PROCESS_NAME)
            win = get_window(hwnd)
            self._resolution_label.setText(f"分辨率: {win.width}×{win.height}")
            self._resolution_label.setStyleSheet("color: green; font-weight: bold;")
        except (WindowNotFoundError, WindowInvalidError):
            self._resolution_label.setText("分辨率: 未检测到窗口")
            self._resolution_label.setStyleSheet("color: red; font-weight: bold;")
        except Exception:
            self._resolution_label.setText("分辨率: 检测异常")
            self._resolution_label.setStyleSheet("color: orange; font-weight: bold;")

    # ------------------------------------------------------------------
    # 系统托盘
    # ------------------------------------------------------------------

    def _setup_tray(self) -> None:
        icon_path = _icon_path()
        icon = QIcon(icon_path) if icon_path else QApplication.style().standardIcon(
            QApplication.style().StandardPixmap.SP_ComputerIcon
        )
        self._tray = QSystemTrayIcon(icon, self)
        self._tray.setToolTip(f"{DEFAULT_TITLE} v{DEFAULT_VERSION}")

        menu = QMenu()
        show_action = menu.addAction("显示/隐藏窗口")
        show_action.triggered.connect(self._toggle_visible)
        menu.addSeparator()
        quit_action = menu.addAction("退出")
        quit_action.triggered.connect(self._quit_app)
        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._toggle_visible()

    def _toggle_visible(self) -> None:
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()

    def _quit_app(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            reply = QMessageBox.question(
                self, "确认退出",
                "脚本仍在运行中，确认停止并退出？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
            self._worker.terminate()
            self._worker.wait(3000)
        self._tray.hide()
        QApplication.quit()

    # ------------------------------------------------------------------
    # closeEvent
    # ------------------------------------------------------------------

    def closeEvent(self, event) -> None:
        event.ignore()
        self.hide()
        self._tray.showMessage(
            f"{DEFAULT_TITLE}",
            "已最小化到系统托盘，右键托盘图标可恢复窗口或退出",
            QSystemTrayIcon.MessageIcon.Information,
            3000,
        )
