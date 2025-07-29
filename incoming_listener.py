import queue
import threading
from flask import Flask, request, jsonify

INCOMING_QUEUE: queue.Queue[str] = queue.Queue()


def _create_app() -> Flask:
    app = Flask(__name__)

    @app.route('/message', methods=['POST'])
    def _message() -> 'Response':
        data = request.get_json() or {}
        text = data.get('message', '')
        if not text:
            return jsonify({'error': 'No message'}), 400
        INCOMING_QUEUE.put(text)
        return jsonify({'status': 'received'})

    return app


def start_listener(port: int) -> threading.Thread:
    """Start a simple HTTP listener on the given port."""
    app = _create_app()
    thread = threading.Thread(
        target=lambda: app.run(host='0.0.0.0', port=port), daemon=True
    )
    thread.start()
    return thread


def get_message(timeout: float | None = 0):
    try:
        return INCOMING_QUEUE.get(timeout=timeout)
    except queue.Empty:
        return None

