import os
import sys
import time
import threading
import socket
import webview
from server import run_server

def find_free_port(start_port=8000):
    for port in range(start_port, start_port + 50):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('127.0.0.1', port))
            s.close()
            return port
        except OSError:
            continue
    return 8000

def start_backend(port, base_dir):
    os.chdir(base_dir)
    try:
        run_server(port)
    except Exception as e:
        print(f"PathDiver Server error: {e}")

def main():
    if getattr(sys, 'frozen', False):
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    port = find_free_port(8000)

    server_thread = threading.Thread(target=start_backend, args=(port, base_dir), daemon=True)
    server_thread.start()
    time.sleep(0.4)

    url = f"http://127.0.0.1:{port}"

    window = webview.create_window(
        title="PathDiver — Intelligent File Traversal & Storage Manager",
        url=url,
        width=1340,
        height=880,
        min_size=(960, 640),
        background_color="#F8FAFC",
        resizable=True
    )

    webview.start(debug=False)

if __name__ == '__main__':
    main()
