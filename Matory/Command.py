import json
import socket as sock_module
import threading
import keyboard
from Runner import MaRunner


class UIRecordController:
    """UI录制热键控制器 — 开始录制后持续接收SDK推送的UI操作消息"""

    def __init__(self, udriver: MaRunner.MatoryConnect):
        self._udriver = udriver
        self._recording = False
        self._recv_thread = None
        self._recv_stop = threading.Event()

    def _receive_loop(self):
        """持续接收SDK推送的UI操作消息"""
        sock = self._udriver.udriver
        sock.settimeout(0.5)
        buf = ""
        while not self._recv_stop.is_set():
            try:
                chunk = sock.recv(65536).decode()
                if not chunk:
                    print("连接已关闭，接收线程退出")
                    break
                buf += chunk
                while buf:
                    try:
                        obj, idx = json.JSONDecoder().raw_decode(buf)
                        print(f"UI事件: {obj}")
                        buf = buf[idx:].lstrip()
                    except json.JSONDecodeError:
                        break
            except sock_module.timeout:
                continue
            except OSError as e:
                print(f"接收出错: {e}")
                break
        sock.settimeout(60)

    def toggle(self):
        if self._recording:
            self._recv_stop.set()
            if self._recv_thread and self._recv_thread.is_alive():
                self._recv_thread.join(timeout=3)
            self._udriver.StopUIRecord()
            print("■ UI录制已停止")
            self._recording = False
        else:
            self._udriver.StartUIRecord()
            print("● UI录制已开始（SDK将持续推送UI操作消息）")
            self._recording = True
            self._recv_stop.clear()
            self._recv_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self._recv_thread.start()

    def run(self, stop_event: threading.Event, toggle_key="ctrl+k", exit_key="ctrl+q"):
        keyboard.add_hotkey(toggle_key, self.toggle)
        keyboard.add_hotkey(exit_key, lambda: stop_event.set())
        print(f"按 Ctrl+K 开始/停止UI录制，按 Ctrl+Q 退出")
        stop_event.wait()
        if self._recording:
            self.toggle()
        keyboard.remove_all_hotkeys()
