import json
import threading
import subprocess
import logging
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from typing import Any, Dict, Optional

import utils
from llm import LLMClass
from audio_player import PygameMediaPlayer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AppGUI:
    """
    A GUI application for generating and playing vibrotactile audio using language models.
    """

    # Class constants
    DEFAULT_NUM_GENERATIONS = 3
    DEFAULT_TEMPERATURE = 0.7
    MAX_TEMPERATURE = 1.0
    MIN_TEMPERATURE = 0.0

    def __init__(self, generator, settings: Dict[str, Any]):
        """
        Initialize the application GUI.
        """
        self.generator = generator
        self.settings = settings
        self.llm = LLMClass(settings)
        self.root = tk.Tk()
        self.root.title("Vibrotactile Generator")
        self.advanced_mode = tk.BooleanVar()

        # Initialize control variables for advanced mode
        self.saved_prompt1_response = None
        self.saved_prompt2_response = None

        # Processing flag to prevent multiple simultaneous operations
        self.processing = False

        # Lock for thread-safe access to shared variables
        self.lock = threading.Lock()

        self.setup_ui()

        # Test connection on startup
        threading.Thread(target=self.test_connection_on_startup, daemon=True).start()

    def setup_ui(self):
        """
        Set up the user interface components.
        """
        self.create_notebook()
        self.create_audio_generation_tab()
        self.create_audio_playback_tab()
        self.create_settings_tab()

    def create_notebook(self):
        """
        Create the notebook (tabbed layout) for the application.
        """
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=10, expand=True)

        self.tabs = {
            "Audio Generation": VerticalScrolledFrame(self.notebook), #ttk.Frame(self.notebook),
            "Audio Playback": ttk.Frame(self.notebook),
            "Settings": ttk.Frame(self.notebook)
        }

        for tab_name, frame in self.tabs.items():
            frame.pack(fill="both", expand=True)
            self.notebook.add(frame, text=tab_name)

    def create_audio_generation_tab(self):
        """
        Create the Audio Generation tab UI components.
        """
        audio_gen_frame = self.tabs["Audio Generation"].interior
        self.audio_gen_frame = audio_gen_frame  # Store reference for advanced mode components

        # Advanced Mode Checkbox
        advanced_mode_checkbox = ttk.Checkbutton(
            audio_gen_frame,
            text="Advanced Mode",
            variable=self.advanced_mode,
            command=self.toggle_advanced_mode
        )
        advanced_mode_checkbox.pack(anchor="w", padx=10, pady=5)

        # Text Input
        self.text_input = scrolledtext.ScrolledText(audio_gen_frame, wrap=tk.WORD, width=50, height=10)
        self.text_input.pack(pady=10)

        # Number of Audio Generations Input (Normal Mode)
        self.num_generations_label = ttk.Label(audio_gen_frame, text="Number of Audio Generations:")
        self.num_generations_entry = ttk.Entry(audio_gen_frame, width=10)
        self.num_generations_entry.insert(0, str(self.DEFAULT_NUM_GENERATIONS))
        self.num_generations_label.pack(pady=5)
        self.num_generations_entry.pack(pady=5)

        # Validate integer input for num_generations_entry
        int_validate_command = self.root.register(self.validate_integer_input)
        self.num_generations_entry.config(validate="key", validatecommand=(int_validate_command, "%P"))

        # Generate Button
        self.generate_button = ttk.Button(audio_gen_frame, text="Start", command=self.generate_output)
        self.generate_button.pack(pady=10)

        # Prompt 1 Frame (contains description)
        self.prompt1_frame = ttk.Frame(audio_gen_frame)
        self.prompt1_description_label = ttk.Label(self.prompt1_frame, text="Description for Prompt 1:")
        self.prompt1_description_entry = scrolledtext.ScrolledText(self.prompt1_frame, wrap=tk.WORD, height=5, width=50)
        self.prompt1_description_label.pack(pady=5)
        self.prompt1_description_entry.pack(pady=5)

        # Horizontal buttons for Prompt 1
        self.button_frame1 = ttk.Frame(audio_gen_frame)
        self.regenerate_button1 = ttk.Button(self.button_frame1, text="Regenerate", command=lambda: self.regenerate_response(1))
        self.edit_with_llm_button1 = ttk.Button(self.button_frame1, text="Regenerate with feedback", command=lambda: self.edit_with_llm(1))
        self.save_button1 = ttk.Button(self.button_frame1, text="Apply", command=lambda: self.save_response(1))  # Renamed from "Next" to "Apply"

        self.regenerate_button1.pack(side="left", padx=5, pady=5)
        self.edit_with_llm_button1.pack(side="left", padx=5, pady=5)
        self.save_button1.pack(side="left", padx=5, pady=5)

        # Prompt 2 Frame (contains description)
        self.prompt2_frame = ttk.Frame(audio_gen_frame)
        self.prompt2_description_label = ttk.Label(self.prompt2_frame, text="Description for Prompt 2:")
        self.prompt2_description_entry = scrolledtext.ScrolledText(self.prompt2_frame, wrap=tk.WORD, height=5, width=50)
        self.prompt2_description_label.pack(pady=5)
        self.prompt2_description_entry.pack(pady=5)

        # Prompt 2 Buttons Frame (contains regenerate and feedback buttons)
        self.prompt2_button_frame = ttk.Frame(audio_gen_frame)
        self.regenerate_button2 = ttk.Button(self.prompt2_button_frame, text="Regenerate", command=lambda: self.regenerate_response(2))
        self.edit_with_llm_button2 = ttk.Button(self.prompt2_button_frame, text="Regenerate with feedback", command=lambda: self.edit_with_llm(2))
        self.regenerate_button2.pack(side="left", padx=5, pady=5)
        self.edit_with_llm_button2.pack(side="left", padx=5, pady=5)

        # Generation Settings Frame (contains number of generations, file name, and duration)
        self.generation_settings_frame = ttk.Frame(audio_gen_frame)
        # Number of Audio Generations Input (Advanced Mode)
        self.num_generations_label_adv = ttk.Label(self.generation_settings_frame, text="Number of Audio Generations:")
        self.num_generations_entry_adv = ttk.Entry(self.generation_settings_frame, width=10)
        self.num_generations_entry_adv.insert(0, str(self.DEFAULT_NUM_GENERATIONS))
        self.num_generations_label_adv.pack(pady=5)
        self.num_generations_entry_adv.pack(pady=5)
        # Validate integer input
        self.num_generations_entry_adv.config(validate="key", validatecommand=(int_validate_command, "%P"))

        # File Name
        self.file_name_label = ttk.Label(self.generation_settings_frame, text="File Name:")
        self.file_name_entry = ttk.Entry(self.generation_settings_frame, width=50)
        self.file_name_label.pack(pady=5)
        self.file_name_entry.pack(pady=5)

        # Duration
        self.duration_label = ttk.Label(self.generation_settings_frame, text="Duration:")
        self.duration_entry = ttk.Entry(self.generation_settings_frame, width=50)
        self.duration_label.pack(pady=5)
        self.duration_entry.pack(pady=5)
        # Validate numeric input for duration_entry
        float_validate_command = self.root.register(self.validate_numeric_input)
        self.duration_entry.config(validate="key", validatecommand=(float_validate_command, "%P"))

        # Finish Button Frame
        self.finish_button_frame = ttk.Frame(audio_gen_frame)
        self.finish_button2 = ttk.Button(self.finish_button_frame, text="Generate", command=lambda: self.save_response(2))
        self.finish_button2.pack(pady=5)

        # Audio Playback and Output Folder Buttons
        self.playback_folder_frame = ttk.Frame(audio_gen_frame)
        self.playback_button = ttk.Button(self.playback_folder_frame, text="Audio Playback", command=lambda: self.notebook.select(self.tabs["Audio Playback"]))
        self.output_folder_button = ttk.Button(self.playback_folder_frame, text="Output Folder", command=self.open_output_folder)

        self.playback_button.pack(side="left", padx=5, pady=5)
        self.output_folder_button.pack(side="left", padx=5, pady=5)
        self.playback_folder_frame.pack(side="bottom", pady=10)

        # Progress Bar
        self.progress_bar = ttk.Progressbar(audio_gen_frame, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(side="bottom", pady=10)

    def create_audio_playback_tab(self):
        """
        Create the Audio Playback tab UI components.
        """
        self.audio_playback_frame = self.tabs["Audio Playback"]
        self.audio_player = PygameMediaPlayer(self.audio_playback_frame)

    def create_settings_tab(self):
        """
        Create the Settings tab UI components.
        """
        settings_frame = self.tabs["Settings"]

        # Primary LLM Settings
        ttk.Label(settings_frame, text="Primary LLM Settings").pack(pady=5)

        # Store each entry field as an instance variable
        self.primary_base_url_entry = self._add_labeled_entry(settings_frame, "Base URL:", "api_url", width=30)
        self.primary_api_key_entry = self._add_labeled_entry(settings_frame, "API Key:", "api_key", show="*", width=30)

        initial_show_api_key = True if self.primary_api_key_entry.cget('show') == '' else False
        button_text = "Hide API Key" if initial_show_api_key else "Show API Key"
        primary_toggle_button = ttk.Button(
            settings_frame,
            text=button_text,
            command=lambda: self.toggle_api_key_visibility(self.primary_api_key_entry, primary_toggle_button)
        )
        primary_toggle_button.pack(pady=5)

        # Model Name, Temperature
        self.primary_model_entry = self._add_labeled_entry(settings_frame, "Model Name:", "model_name", width=30)
        self.primary_temperature_entry = self._add_labeled_entry(settings_frame, "Temperature:", "temperature", width=10)
        # Validate numeric input for primary_temperature_entry
        float_validate_command = self.root.register(self.validate_numeric_input)
        self.primary_temperature_entry.config(validate="key", validatecommand=(float_validate_command, "%P"))

        # Status Label
        self.status_label = ttk.Label(settings_frame, text="Disconnected", foreground="red")
        self.status_label.pack(pady=5)

        # Apply Button (store as instance variable)
        self.apply_button = ttk.Button(settings_frame, text="Apply Settings", command=self.apply_settings)
        self.apply_button.pack(pady=10)

        # Audio Save Path
        save_path_label = ttk.Label(settings_frame, text="Audio Save Path:")
        save_path_label.pack(pady=5)
        self.save_path_entry = ttk.Entry(settings_frame, width=30)
        self.save_path_entry.insert(0, self.settings.get("default_save_path", ""))
        self.save_path_entry.pack(pady=5)
        browse_button = ttk.Button(settings_frame, text="Browse", command=self.browse_save_path)
        browse_button.pack(pady=5)

    def _add_labeled_entry(self, parent, label_text: str, setting_key: str, show: Optional[str] = None, width: int = 20) -> ttk.Entry:
        """
        Helper method to add a labeled entry field to a parent widget.
        """
        label = ttk.Label(parent, text=label_text)
        label.pack(pady=5)
        entry = ttk.Entry(parent, width=width, show=show)
        entry.insert(0, self.settings.get(setting_key, ""))
        entry.pack(pady=5)
        return entry

    def validate_numeric_input(self, value_if_allowed: str) -> bool:
        """
        Validate that the input is a valid float.
        """
        if value_if_allowed == "":
            return True
        try:
            float(value_if_allowed)
            return True
        except ValueError:
            return False

    def validate_integer_input(self, value_if_allowed: str) -> bool:
        """
        Validate that the input is a valid integer.
        """
        if value_if_allowed == "":
            return True
        return value_if_allowed.isdigit()

    def toggle_advanced_mode(self):
        """
        Toggle the visibility of advanced mode widgets.
        """
        if self.advanced_mode.get():
            # Hide normal mode widgets
            self.num_generations_label.pack_forget()
            self.num_generations_entry.pack_forget()
            # Show advanced mode widgets
            self.prompt1_frame.pack(pady=5)
            self.button_frame1.pack(pady=5)
            self.prompt2_frame.pack(pady=5)
            self.prompt2_button_frame.pack(pady=5)
            self.generation_settings_frame.pack(pady=5)
            self.finish_button_frame.pack(pady=5)
        else:
            # Hide advanced mode widgets
            self.prompt1_frame.pack_forget()
            self.button_frame1.pack_forget()
            self.prompt2_frame.pack_forget()
            self.prompt2_button_frame.pack_forget()
            self.generation_settings_frame.pack_forget()
            self.finish_button_frame.pack_forget()
            # Show normal mode widgets
            self.num_generations_label.pack(pady=5)
            self.num_generations_entry.pack(pady=5)

    def toggle_api_key_visibility(self, entry: ttk.Entry, button: ttk.Button):
        """
        Toggle the visibility of the API key entry field.
        """
        if entry.cget("show") == "*":
            entry.config(show="")
            button.config(text="Hide API Key")
        else:
            entry.config(show="*")
            button.config(text="Show API Key")

    def browse_save_path(self):
        """
        Open a directory dialog to select save path.
        """
        directory = filedialog.askdirectory()
        if directory:
            self.save_path_entry.delete(0, tk.END)
            self.save_path_entry.insert(0, directory)

    def regenerate_response(self, prompt_num: int):
        """
        Regenerate the response for a specific prompt.
        """
        if self.processing:
            self.show_warning("An operation is already in progress. Please wait.")
            return

        self.processing = True
        self.disable_buttons()
        threading.Thread(target=self._regenerate_response_thread, args=(prompt_num,), daemon=True).start()

    def _regenerate_response_thread(self, prompt_num: int):
        """
        Thread target for regenerating a response.
        """
        try:
            if prompt_num == 1:
                input_text = self.text_input.get("1.0", tk.END).strip()
                if not input_text:
                    self.show_warning("Please enter a tactile sensation description.")
                    return
                new_response = self.llm.generate_description_prompt1(input_text)
                response_data = json.loads(new_response)
                with self.lock:
                    self.saved_prompt1_response = new_response
                self.update_prompt1_fields(response_data)
            elif prompt_num == 2:
                prompt1_description = self.prompt1_description_entry.get("1.0", tk.END).strip()
                if not prompt1_description:
                    self.show_warning("Prompt 1 description is empty. Please generate or enter a description.")
                    return
                new_response = self.llm.generate_description_prompt2(prompt1_description)
                response_data = json.loads(new_response)
                with self.lock:
                    self.saved_prompt2_response = new_response
                self.update_prompt2_fields(response_data)
            else:
                logger.error(f"Regeneration for prompt {prompt_num} is not supported.")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response for prompt {prompt_num}: {e}")
            self.show_error(f"Invalid response from LLM for prompt {prompt_num}. Please try again.")
        except Exception as e:
            logger.error(f"Failed to regenerate response for prompt {prompt_num}: {e}")
            self.show_error(f"Failed to regenerate response for prompt {prompt_num}: {e}")
        finally:
            self.processing = False
            self.enable_buttons()

    def update_prompt1_fields(self, data: Dict[str, Any]):
        """
        Update the Prompt 1 fields in a thread-safe manner.
        """
        self.root.after(0, self._update_prompt1_fields_ui, data)

    def _update_prompt1_fields_ui(self, data: Dict[str, Any]):
        """
        Update Prompt 1 fields on the main thread.
        """
        self.prompt1_description_entry.delete("1.0", tk.END)
        self.prompt1_description_entry.insert("1.0", data.get("description", ""))

        # Update File Name and Duration in Generation Settings Frame
        self.file_name_entry.delete(0, tk.END)
        self.file_name_entry.insert(0, data.get("name", ""))

        self.duration_entry.delete(0, tk.END)
        duration = data.get("duration", "")
        if isinstance(duration, (int, float, str)):
            self.duration_entry.insert(0, str(duration))

    def update_prompt2_fields(self, data: Dict[str, Any]):
        """
        Update the Prompt 2 fields in a thread-safe manner.
        """
        self.root.after(0, self._update_prompt2_fields_ui, data)

    def _update_prompt2_fields_ui(self, data: Dict[str, Any]):
        """
        Update Prompt 2 fields on the main thread.
        """
        self.prompt2_description_entry.delete("1.0", tk.END)
        self.prompt2_description_entry.insert("1.0", data.get("description", ""))

    def save_response(self, prompt_num: int):
        """
        Save the response for a given prompt and proceed accordingly.
        """
        if self.processing:
            self.show_warning("An operation is already in progress. Please wait.")
            return

        if prompt_num == 1:
            prompt1_description = self.prompt1_description_entry.get("1.0", tk.END).strip()
            if not prompt1_description:
                self.show_warning("Prompt 1 description is empty. Please generate or enter a description.")
                return
            # Proceed to generate Prompt 2
            self.processing = True
            self.disable_buttons()
            threading.Thread(target=self._generate_prompt2_thread, daemon=True).start()
        elif prompt_num == 2:
            prompt2_description = self.prompt2_description_entry.get("1.0", tk.END).strip()
            if not prompt2_description:
                self.show_warning("Prompt 2 description is empty. Please generate or enter a description.")
                return
            response_data = {
                "description": prompt2_description
            }
            try:
                # Ensure that the JSON can be serialized properly
                json_string = json.dumps(response_data)
                json.loads(json_string)
                with self.lock:
                    self.saved_prompt2_response = json_string
                self.show_info("Advanced mode responses finalized. Proceeding with audio generation.")
                # Proceed to audio generation
                self.processing = True
                self.disable_buttons()
                threading.Thread(target=self.continue_audio_generation, daemon=True).start()
            except json.JSONDecodeError as e:
                logger.error(f"Failed to serialize Prompt 2 data: {e}")
                self.show_error(f"Invalid characters in Prompt 2 description. Please remove any invalid characters.")
                self.processing = False
                self.enable_buttons()
        else:
            # Handle other prompt numbers if needed
            pass

    def _generate_prompt2_thread(self):
        """
        Thread target for generating Prompt 2 in advanced mode.
        """
        try:
            prompt1_description = self.prompt1_description_entry.get("1.0", tk.END).strip()
            if not prompt1_description:
                self.show_warning("Prompt 1 description is empty. Please generate or enter a description.")
                return
            new_response = self.llm.generate_description_prompt2(self.saved_prompt1_response)
            response_data = json.loads(new_response)
            with self.lock:
                self.saved_prompt2_response = new_response
            if self.advanced_mode.get():
                self.update_prompt2_fields(response_data)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response for prompt 2: {e}")
            self.show_error(f"Invalid response from LLM for prompt 2. Please try again.")
        except Exception as e:
            logger.error(f"Failed to generate response for prompt 2: {e}")
            self.show_error(f"Failed to generate response for prompt 2: {e}")
        finally:
            self.processing = False
            self.enable_buttons()

    def test_connection_on_startup(self):
        """
        Test the LLM connection on startup.
        """
        self.update_status_label("Connecting...", "yellow")
        if self.llm.test_llm_connection():
            self.update_status_label("Connected", "green")
        else:
            self.update_status_label("Connection Failed", "red")
            self.show_warning("Could not connect to the LLM on startup. Please check your settings.")

    def apply_settings(self):
        """
        Apply the updated settings and attempt to update connection status.
        """
        if self.processing:
            self.show_warning("An operation is already in progress. Please wait.")
            return

        self.processing = True
        self.disable_buttons()
        threading.Thread(target=self._apply_settings_thread, daemon=True).start()

    def _apply_settings_thread(self):
        """
        Thread target for applying settings.
        """
        try:
            primary_url = self.primary_base_url_entry.get().strip()
            primary_api_key = self.primary_api_key_entry.get().strip()
            primary_model = self.primary_model_entry.get().strip()
            primary_temperature = self.primary_temperature_entry.get().strip()

            # Validate inputs
            if not primary_url or not primary_model or not primary_temperature:
                self.show_warning("Please fill in all LLM settings.")
                return

            try:
                primary_temperature = float(primary_temperature)
                if not (self.MIN_TEMPERATURE <= primary_temperature <= self.MAX_TEMPERATURE):
                    raise ValueError("Temperature must be between 0 and 1.")
            except ValueError as e:
                self.show_error(f"Invalid temperature: {e}")
                return

            self.llm.update_llm_settings(primary_temperature, primary_url, primary_api_key, primary_model)
            self.update_status_label("Connecting...", "yellow")
            if self.llm.test_llm_connection():
                self.update_status_label("Connected", "green")
            else:
                self.update_status_label("Connection Failed", "red")
                self.show_warning("Could not connect to the LLM. Please check your settings.")
        except Exception as e:
            self.update_status_label("Error", "red")
            self.show_error(f"Failed to apply settings: {e}")
        finally:
            self.processing = False
            self.enable_buttons()

    def update_status_label(self, text: str, color: str):
        """
        Update the status label in a thread-safe manner.
        """
        self.root.after(0, self.status_label.config, {'text': text, 'foreground': color})

    def generate_output(self):
        """
        Generate audio with advanced mode handling.
        """
        if self.processing:
            self.show_warning("An operation is already in progress. Please wait.")
            return

        self.processing = True
        self.disable_buttons()
        threading.Thread(target=self._generate_output_thread, daemon=True).start()

    def _generate_output_thread(self):
        """
        Thread target for generating output.
        """
        try:
            user_input = self.text_input.get("1.0", tk.END).strip()
            if self.advanced_mode.get():
                num_generations = self.num_generations_entry_adv.get().strip()
            else:
                num_generations = self.num_generations_entry.get().strip()
            save_path = self.save_path_entry.get().strip()

            # Validate inputs
            if not user_input:
                self.show_warning("Please enter a tactile sensation description.")
                return

            if not num_generations.isdigit() or int(num_generations) <= 0:
                self.show_warning("Please enter a valid positive integer for the number of generations.")
                return

            if not save_path:
                self.show_warning("Please specify an audio save path in Settings.")
                return

            num_generations = int(num_generations)
            self.root.after(0, self.progress_bar.config, {'maximum': num_generations, 'value': 0})

            generated_files = []

            # Generate Prompt 1
            self.saved_prompt1_response = self.generate_response_with_advanced_mode(user_input, 1)
            if not self.saved_prompt1_response:
                raise ValueError("Prompt 1 generation failed or returned invalid JSON.")

            prompt1_json = json.loads(self.saved_prompt1_response)
            self.update_prompt1_fields(prompt1_json)

            # Generate Prompt 2
            self.saved_prompt2_response = self.generate_response_with_advanced_mode(self.saved_prompt1_response, 2)
            if not self.saved_prompt2_response:
                raise ValueError("Prompt 2 generation failed or returned invalid JSON.")

            prompt2_json = json.loads(self.saved_prompt2_response)
            self.update_prompt2_fields(prompt2_json)

            if self.advanced_mode.get():
                # Wait for user to click 'Finish' (save_response(2))
                pass
            else:
                # Proceed to audio generation
                file_name = prompt1_json.get("name", "default_name")
                duration = prompt1_json.get("duration", 0)
                prompt2_text = prompt2_json.get("description", "")
                self.generate_audio_files(prompt2_text, duration, file_name, num_generations, save_path, generated_files)
        except Exception as e:
            logger.error(f"Error during audio generation: {e}")
            self.show_error(str(e))
        finally:
            if not self.advanced_mode.get():
                # Reset input fields after generation
                self.reset_input_fields()
            # Set processing to False and enable buttons regardless of mode
            self.processing = False
            self.enable_buttons()

    def continue_audio_generation(self):
        """
        Continue with audio generation after advanced mode inputs are finalized.
        """
        try:
            prompt1_json = json.loads(self.saved_prompt1_response)
            file_name = self.file_name_entry.get().strip() or prompt1_json.get("name", "default_name")
            duration_str = self.duration_entry.get().strip()
            if not duration_str:
                duration = prompt1_json.get("duration", 0)
            else:
                try:
                    duration = float(duration_str)
                except ValueError:
                    self.show_warning("Please enter a valid number for duration.")
                    return

            if duration <= 0:
                self.show_warning("Duration must be a positive number.")
                return

            prompt2_json = json.loads(self.saved_prompt2_response)
            prompt2_text = prompt2_json.get("description", "")
            num_generations_str = self.num_generations_entry_adv.get().strip()
            if not num_generations_str.isdigit() or int(num_generations_str) <= 0:
                self.show_warning("Please enter a valid positive integer for the number of generations.")
                return
            num_generations = int(num_generations_str)
            save_path = self.save_path_entry.get().strip()
            if not save_path:
                self.show_warning("Please specify an audio save path in Settings.")
                return
            generated_files = []
            self.generate_audio_files(prompt2_text, duration, file_name, num_generations, save_path, generated_files)
        except Exception as e:
            logger.error(f"Error during audio generation: {e}")
            self.show_error(str(e))
        finally:
            if not self.advanced_mode.get():
                self.reset_input_fields()
            self.processing = False
            self.enable_buttons()

    def generate_response_with_advanced_mode(self, prompt_text: str, prompt_num: int) -> Optional[str]:
        """
        Generate or regenerate the response based on the prompt number.
        """
        try:
            if prompt_num == 1:
                response_text = self.llm.generate_description_prompt1(prompt_text)
                response_data = json.loads(response_text)
                with self.lock:
                    self.saved_prompt1_response = response_text
                self.update_prompt1_fields(response_data)
            else:
                response_text = self.llm.generate_description_prompt2(prompt_text)
                response_data = json.loads(response_text)
                with self.lock:
                    self.saved_prompt2_response = response_text
                self.update_prompt2_fields(response_data)
            return response_text
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response for prompt {prompt_num}: {e}")
            self.show_error(f"Invalid response from LLM for prompt {prompt_num}. Please try again.")
            return None
        except Exception as e:
            logger.error(f"Failed to generate response for prompt {prompt_num}: {e}")
            self.show_error(f"Failed to generate response for prompt {prompt_num}: {e}")
            return None
        finally:
            if self.advanced_mode.get():
                # Only reset processing flag and enable buttons in advanced mode
                self.processing = False
                self.enable_buttons()

    def generate_audio_files(self, prompt_text, duration, file_name, num_generations, save_path, generated_files):
        """
        Generate audio files based on the given prompt.
        """
        try:
            if duration <= 0:
                raise ValueError("Duration must be a positive number.")

            if not os.path.exists(save_path):
                os.makedirs(save_path)

            self.generator.update_model_settings(duration)

            for iteration in range(num_generations):
                output_cpu = self.generator.generate_model(prompt_text)
                generated_file_name = f"{file_name}_{iteration}.wav"
                utils.save_audio_file(output_cpu, file_name, save_path, iteration)
                generated_files.append(generated_file_name)

                # Update progress bar
                self.update_progress_bar(iteration + 1)

            self.show_info("Audio generation completed successfully!")
            self.audio_player.audio_generation_done(generated_files)
        except Exception as e:
            logger.error(f"Error during audio generation: {e}")
            self.show_error(f"Error during audio generation: {e}")

    def edit_with_llm(self, prompt_num: int):
        """
        Create a popup window for providing feedback to modify the prompt.
        """
        if self.processing:
            self.show_warning("An operation is already in progress. Please wait.")
            return

        popup = tk.Toplevel(self.root)
        popup.title(f"Provide feedback to modify prompt {prompt_num}")

        # Add instruction label and text box
        ttk.Label(popup, text="Provide feedback to modify this prompt:").pack(pady=5)
        instructions_text = scrolledtext.ScrolledText(popup, wrap=tk.WORD, height=10, width=40)
        instructions_text.pack(pady=5)

        # Define the confirm button behavior
        def confirm():
            instructions = instructions_text.get("1.0", tk.END).strip()
            if not instructions:
                self.show_error("Please provide instructions for the LLM.")
                return
            popup.destroy()
            self.processing = True
            self.disable_buttons()
            threading.Thread(target=self.process_llm_edit, args=(prompt_num, instructions), daemon=True).start()

        # Add confirm button
        ttk.Button(popup, text="Confirm and regenerate", command=confirm).pack(pady=5)

    def process_llm_edit(self, prompt_num: int, instructions: str):
        """
        Process the LLM edit based on user instructions.
        """
        try:
            if prompt_num == 1:
                response_data = {
                    "description": self.prompt1_description_entry.get("1.0", tk.END).strip(),
                    "name": self.file_name_entry.get().strip(),
                    "duration": self.duration_entry.get().strip()
                }
            elif prompt_num == 2:
                response_data = {
                    "description": self.prompt2_description_entry.get("1.0", tk.END).strip()
                }
            else:
                self.show_error("Invalid prompt number.")
                return

            try:
                # Ensure that the JSON can be serialized properly
                json_string = json.dumps(response_data)
                json.loads(json_string)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to serialize Prompt {prompt_num} data: {e}")
                self.show_error(f"Invalid characters in Prompt {prompt_num} description. Please remove any invalid characters.")
                return

            edited_json = self.llm.generate_edited_prompt(json_string, instructions)
            edited_data = json.loads(edited_json)

            if prompt_num == 1:
                self.update_prompt1_fields(edited_data)
            elif prompt_num == 2:
                self.update_prompt2_fields(edited_data)

            self.show_info(f"Prompt {prompt_num} successfully updated!")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse edited prompt {prompt_num}: {e}")
            self.show_error(f"Invalid response from LLM while editing prompt {prompt_num}. Please try again.")
        except Exception as e:
            logger.error(f"Failed to edit Prompt {prompt_num}: {e}")
            self.show_error(f"Failed to edit Prompt {prompt_num}: {e}")
        finally:
            self.processing = False
            self.enable_buttons()

    def update_progress_bar(self, value: int):
        """
        Update the progress bar in a thread-safe manner.
        """
        self.root.after(0, self.progress_bar.config, {'value': value})

    def reset_input_fields(self):
        """
        Clears the text input and prompt responses.
        """
        self.root.after(0, self._reset_input_fields_ui)

    def _reset_input_fields_ui(self):
        """
        Reset input fields on the main thread.
        """
        self.text_input.delete("1.0", tk.END)
        self.prompt1_description_entry.delete("1.0", tk.END)
        self.prompt2_description_entry.delete("1.0", tk.END)
        self.num_generations_entry.delete(0, tk.END)
        self.num_generations_entry.insert(0, str(self.DEFAULT_NUM_GENERATIONS))
        self.num_generations_entry_adv.delete(0, tk.END)
        self.num_generations_entry_adv.insert(0, str(self.DEFAULT_NUM_GENERATIONS))
        self.file_name_entry.delete(0, tk.END)
        self.duration_entry.delete(0, tk.END)

    def disable_buttons(self):
        """
        Disable buttons to prevent user interaction during processing.
        """
        self.root.after(0, self._disable_buttons_ui)

    def _disable_buttons_ui(self):
        self.generate_button.config(state=tk.DISABLED)
        self.regenerate_button1.config(state=tk.DISABLED)
        self.edit_with_llm_button1.config(state=tk.DISABLED)
        self.save_button1.config(state=tk.DISABLED)
        self.regenerate_button2.config(state=tk.DISABLED)
        self.edit_with_llm_button2.config(state=tk.DISABLED)
        self.finish_button2.config(state=tk.DISABLED)
        self.apply_settings_button_state(tk.DISABLED)

    def enable_buttons(self):
        """
        Enable buttons after processing is complete.
        """
        self.root.after(0, self._enable_buttons_ui)

    def _enable_buttons_ui(self):
        self.generate_button.config(state=tk.NORMAL)
        self.regenerate_button1.config(state=tk.NORMAL)
        self.edit_with_llm_button1.config(state=tk.NORMAL)
        self.save_button1.config(state=tk.NORMAL)
        self.regenerate_button2.config(state=tk.NORMAL)
        self.edit_with_llm_button2.config(state=tk.NORMAL)
        self.finish_button2.config(state=tk.NORMAL)
        self.apply_settings_button_state(tk.NORMAL)

    def apply_settings_button_state(self, state):
        """
        Set the state of the apply settings button.
        """
        self.root.after(0, self.apply_button.config, {'state': state})

    def select_audio_file(self):
        """
        Handles the file selection for the audio player.
        """
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav")])
        if file_path:
            self.audio_player.load_audio(file_path)

    def open_output_folder(self):
        """
        Opens the file explorer in the output directory.
        """
        directory = self.save_path_entry.get()
        if directory:
            # Convert to absolute path
            directory = os.path.abspath(directory)
            if os.path.isdir(directory):
                try:
                    # Use subprocess to open the directory with explorer
                    subprocess.Popen(f'explorer "{directory}"', shell=True)
                except Exception as e:
                    logger.error(f"Failed to open directory {directory}: {e}")
                    self.show_error(f"Failed to open directory: {e}")
            else:
                self.show_warning("Invalid directory. Please select a valid output folder in Settings.")
        else:
            self.show_warning("Invalid directory. Please select a valid output folder in Settings.")

    def show_info(self, message: str):
        """
        Show an informational message in a thread-safe manner.
        """
        self.root.after(0, messagebox.showinfo, "Info", message)

    def show_warning(self, message: str):
        """
        Show a warning message in a thread-safe manner.
        """
        self.root.after(0, messagebox.showwarning, "Warning", message)

    def show_error(self, message: str):
        """
        Show an error message in a thread-safe manner.
        """
        self.root.after(0, messagebox.showerror, "Error", message)

    def run(self):
        """
        Run the main event loop of the application.
        """
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        """
        Handle application shutdown.
        """
        # Perform any necessary cleanup
        self.root.destroy()


# Relying on https://stackoverflow.com/questions/16188420/tkinter-scrollbar-for-frame
class VerticalScrolledFrame(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)

        scrollbar = ttk.Scrollbar(self, orient=tk.constants.VERTICAL)
        scrollbar.pack(fill=tk.constants.Y, side=tk.constants.RIGHT, expand=tk.constants.FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0, yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.constants.LEFT, fill=tk.constants.BOTH, expand=tk.constants.TRUE)
        scrollbar.config(command=canvas.yview)

        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        self.interior = interior = ttk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior, anchor=tk.constants.NW)

        def _configure_interior(event):
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)
