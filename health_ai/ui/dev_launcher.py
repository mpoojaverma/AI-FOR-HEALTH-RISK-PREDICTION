import sys
import os
import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ReloadHandler(FileSystemEventHandler):
    def __init__(self, script):
        self.script = script
        self.process = None
        self.start_app()

    def start_app(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
        print(f"\n[HOT RELOAD] Starting {self.script}...")
        self.process = subprocess.Popen([sys.executable, self.script])

    def on_modified(self, event):
        if event.src_path.endswith(".py") or event.src_path.endswith(".css"):
            print(f"\n[HOT RELOAD] Change detected in {os.path.basename(event.src_path)}")
            self.start_app()

if __name__ == "__main__":
    # Path to your main app
    target_script = "main_app.py" 
    
    # Watch the entire project root
    watch_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    event_handler = ReloadHandler(target_script)
    observer = Observer()
    observer.schedule(event_handler, watch_path, recursive=True)
    observer.start()

    print(f"🔥 Hot Reload Active! Watching: {watch_path}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()