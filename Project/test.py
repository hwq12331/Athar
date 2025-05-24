import subprocess
import threading
import time
import shutil
import os

NODE_PATH = shutil.which("node")
MAGNET_SCRIPT = os.path.abspath("magnet.mjs")  # This should be your working seeder.mjs

def run_and_capture_magnet(file_path):
    proc = subprocess.Popen(
        [NODE_PATH, MAGNET_SCRIPT, file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    magnet_uri = None

    def stream_logs():
        nonlocal magnet_uri
        capture_next = False

        for line in proc.stdout:
            line = line.strip()
            print("🪵 JS LINE:", line)

            if capture_next:
                magnet_uri = line
                capture_next = False

            if "MAGNET URI" in line:
                capture_next = True


    thread = threading.Thread(target=stream_logs)
    thread.start()
    thread.join(timeout=15)

    print("\n🧪 FINAL magnet_uri in Python:", magnet_uri)
    return magnet_uri or "⚠️ Magnet URI not found."

# Replace this with any valid file path
test_file = "combinepdf.pdf"
run_and_capture_magnet(test_file)
