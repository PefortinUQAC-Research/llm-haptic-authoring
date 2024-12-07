from gui import AppGUI
from logic import VibrotactileGenerator
from config import SETTINGS

def main():
    generator = VibrotactileGenerator()  # Core logic component
    app = AppGUI(generator, SETTINGS)    # GUI component with injected logic and settings
    app.run()                            # Start the GUI loop

if __name__ == "__main__":
    main()
