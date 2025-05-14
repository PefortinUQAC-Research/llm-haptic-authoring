import sys
if getattr(sys, 'frozen', False):
    import pyi_splash
from gui import AppGUI
from logic import VibrotactileGenerator
from config import SETTINGS
from log import write_logs_to_file
import os

def main():
    # Create log/output path if not already present.
    if not os.path.exists(SETTINGS['log_path']):
        os.makedirs(SETTINGS['log_path'])
    if not os.path.exists(SETTINGS['default_save_path']):
        os.makedirs(SETTINGS['default_save_path'])

    generator = VibrotactileGenerator()  # Core logic component
    app = AppGUI(generator, SETTINGS)    # GUI component with injected logic and settings
    if getattr(sys, 'frozen', False):
        pyi_splash.close()
    app.run()                            # Start the GUI loop

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
    finally:
        i = 0
        if 'USERNAME' in os.environ:
            prefix = f"{os.environ['USERNAME']}_"
        elif 'USER' in os.environ:
            prefix = f"{os.environ['USER']}_"
        else:
            prefix = "unknown_"
        while os.path.exists(f"{SETTINGS['log_path']}/{prefix}{SETTINGS['log_name']}_{i}.csv"):
            i += 1
        write_logs_to_file(f"{SETTINGS['log_path']}/{prefix}{SETTINGS['log_name']}_{i}.csv")
