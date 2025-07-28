import sys
import platform
from typing import Dict

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
)

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


class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Echo")
        self.resize(600, 400)

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
        layout.addWidget(self.log)
        layout.addLayout(bottom)
        self.setLayout(layout)

    def append_log(self, text: str) -> None:
        self.log.append(text)

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
                self.append_log(f"Bot: {reply}")

            elif mode == "command":
                cmd = call_anythingllm(text)
                summary = cmd.get("summary", "")
                ok = QMessageBox.question(self, "Run command", summary)
                if ok == QMessageBox.Yes:
                    result = execute_parsed_command(cmd)
                    self.append_log(str(result))

            elif mode == "script":
                script = create_script(text, os_type, target)
                ok = QMessageBox.question(
                    self,
                    "Run script",
                    f"{script}\n\nExecute?",
                )
                if ok == QMessageBox.Yes:
                    result = execute_script(script, os_type)
                    self.append_log(str(result))

            else:  # execute plan
                plan = create_plan(text)
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
