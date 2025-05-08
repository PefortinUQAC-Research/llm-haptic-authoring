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
    app.run()                            # Start the GUI loop

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
    finally:
        i = 0
        while os.path.exists(f"{SETTINGS['log_path']}/{SETTINGS['log_name']}-{i}.csv"):
            i += 1
        write_logs_to_file(f"{SETTINGS['log_path']}/{SETTINGS['log_name']}-{i}.csv")
