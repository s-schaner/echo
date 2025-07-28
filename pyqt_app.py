import sys
import platform
import json
import os
import time
from typing import Dict, List

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QComboBox,
    QMessageBox,
    QListWidget,
    QLabel,
)
from PyQt5.QtCore import Qt

from planner import create_plan
from executor import execute_plan
from chat_interface import (
    CONFIG,
    call_lmstudio,
    call_openai,
    call_anythingllm,
    execute_parsed_command,
    create_script,
    execute_script,
)

SCRIPT_FILE = os.path.join("logs", "scripts.json")


def load_script_history() -> List[Dict]:
    if os.path.exists(SCRIPT_FILE):
        try:
            with open(SCRIPT_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_script_history(history: List[Dict]) -> None:
    os.makedirs(os.path.dirname(SCRIPT_FILE), exist_ok=True)
    with open(SCRIPT_FILE, "w") as f:
        json.dump(history, f, indent=2)


def add_script_history(script: str, os_type: str) -> None:
    history = load_script_history()
    history.insert(0, {"script": script, "os": os_type, "time": time.time()})
    save_script_history(history)


class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Echo")
        self.resize(800, 600)

        self.mode_box = QComboBox()
        self.mode_box.addItems(["chat", "execute", "command", "script"])

        self.os_box = QComboBox()
        self.os_box.addItems(["linux", "windows"])
        if platform.system().lower().startswith("win"):
            self.os_box.setCurrentText("windows")
        else:
            self.os_box.setCurrentText("linux")

        self.target_box = QComboBox()
        self.target_box.addItems(["lmstudio", "openai"])

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.llm_log = QTextEdit()
        self.llm_log.setReadOnly(True)

        self.script_list = QListWidget()
        self.run_script_btn = QPushButton("Run Selected")
        self.run_script_btn.clicked.connect(self.run_selected_script)
        self.script_history: List[Dict] = load_script_history()
        self.refresh_scripts()

        self.input = QLineEdit()
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.handle_send)

        top = QHBoxLayout()
        top.addWidget(self.mode_box)
        top.addWidget(self.os_box)
        top.addWidget(self.target_box)

        bottom = QHBoxLayout()
        bottom.addWidget(self.input)
        bottom.addWidget(self.send_btn)

        layout = QVBoxLayout()
        layout.addLayout(top)
        layout.addWidget(QLabel("Chat Log"))
        layout.addWidget(self.log)
        layout.addWidget(QLabel("LLM Output"))
        layout.addWidget(self.llm_log)
        layout.addLayout(bottom)
        layout.addWidget(QLabel("Scripts"))
        layout.addWidget(self.script_list)
        layout.addWidget(self.run_script_btn)
        self.setLayout(layout)

    def append_log(self, text: str) -> None:
        self.log.append(text)

    def append_llm_output(self, text: str) -> None:
        self.llm_log.append(text)

    def refresh_scripts(self) -> None:
        self.script_list.clear()
        self.script_history = load_script_history()
        for item in self.script_history:
            snippet = (item.get("script", "").splitlines()[0])[:60]
            self.script_list.addItem(snippet)

    def run_selected_script(self) -> None:
        row = self.script_list.currentRow()
        if row < 0 or row >= len(self.script_history):
            return
        item = self.script_history[row]
        script = item.get("script", "")
        os_type = item.get("os", self.os_box.currentText())
        ok = QMessageBox.question(
            self,
            "Run script",
            f"{script}\n\nExecute?",
        )
        if ok == QMessageBox.Yes:
            result = execute_script(script, os_type)
            self.append_log(str(result))
            add_script_history(script, os_type)
            self.refresh_scripts()

    def handle_send(self):
        text = self.input.text().strip()
        if not text:
            return
        mode = self.mode_box.currentText()
        os_type = self.os_box.currentText()
        target = self.target_box.currentText()
        self.append_log(f"You: {text}")
        self.input.clear()

        try:
            if mode == "chat":
                messages = [
                    {"role": "user", "content": text},
                ]
                if target == "openai":
                    reply = call_openai(messages)
                else:
                    reply = call_lmstudio(messages)
                self.append_llm_output(reply)
                self.append_log(f"Bot: {reply}")

            elif mode == "command":
                cmd = call_anythingllm(text)
                summary = cmd.get("summary", "")
                self.append_llm_output(summary)
                ok = QMessageBox.question(self, "Run command", summary)
                if ok == QMessageBox.Yes:
                    result = execute_parsed_command(cmd)
                    self.append_log(str(result))

            elif mode == "script":
                script = create_script(text, os_type, target)
                self.append_llm_output(script)
                ok = QMessageBox.question(
                    self,
                    "Run script",
                    f"{script}\n\nExecute?",
                )
                if ok == QMessageBox.Yes:
                    result = execute_script(script, os_type)
                    self.append_log(str(result))
                    add_script_history(script, os_type)
                    self.refresh_scripts()

            else:  # execute plan
                plan = create_plan(text)
                self.append_llm_output(str(plan))
                ok = QMessageBox.question(
                    self,
                    "Execute plan",
                    f"{plan}\n\nExecute?",
                )
                if ok == QMessageBox.Yes:
                    results = execute_plan(plan)
                    self.append_log(str(results))
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))


def main() -> None:
    app = QApplication(sys.argv)
    win = ChatWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
