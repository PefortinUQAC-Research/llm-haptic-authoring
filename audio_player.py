import tkinter as tk
from tkinter import ttk, messagebox
import pygame
import os
import subprocess
import logging

logger = logging.getLogger(__name__)

class PygameMediaPlayer:
    """
    A media player for playing audio files using pygame, integrated into a Tkinter GUI.
    """

    def __init__(self, root):
        """
        Initialize the media player.
        """
        try:
            pygame.mixer.init()
        except Exception as e:
            logger.error(f"Failed to initialize pygame mixer: {e}")
            messagebox.showerror("Error", f"Failed to initialize audio player: {e}")
            return  # Do not proceed if mixer fails to initialize
        self.root = root
        self.current_audio = None
        self.recently_generated = set()
        
        # Create UI for player
        self.create_ui()
        # Populate audio list
        self.update_audio_list()

    def create_ui(self):
        """
        Create the user interface for the media player.
        """
        # Frame for Pygame Player
        self.frame = ttk.Frame(self.root)
        self.frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Inner Frame for Play, Stop, and Volume Slider
        control_frame = ttk.Frame(self.frame)
        control_frame.pack(pady=10)

        # Play and Stop Buttons
        self.play_button = ttk.Button(control_frame, text="Play", command=self.play)
        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop)

        self.play_button.grid(row=0, column=0, padx=5, pady=5)
        self.stop_button.grid(row=0, column=1, padx=5, pady=5)

        # Time Label (Seconds/Milliseconds)
        self.time_label = ttk.Label(control_frame, text="0.000s / 0.000s")
        self.time_label.grid(row=1, column=0, columnspan=2, pady=5)

        # Volume Slider
        self.volume_slider = tk.Scale(control_frame, from_=0, to=1, resolution=0.01, orient="horizontal", command=self.set_volume)
        self.volume_slider.set(0.5)  # Set default volume to 50%
        self.volume_slider.grid(row=2, column=0, columnspan=3, pady=10)
        self.volume_slider.config(label="Volume")

        # Filter Checkbutton
        self.filter_var = tk.BooleanVar(value=True)  # Set default value to True
        self.filter_checkbutton = ttk.Checkbutton(
            self.frame,
            text="Show Recently Generated Only",
            variable=self.filter_var,
            command=self.update_audio_list
        )
        self.filter_checkbutton.pack(pady=5)

        # Audio Listbox
        self.audio_listbox = tk.Listbox(self.frame, selectmode=tk.SINGLE)
        self.audio_listbox.pack(fill="both", expand=True, padx=5, pady=10)
        self.audio_listbox.bind("<<ListboxSelect>>", self.on_audio_select)

        # Refresh Button
        self.refresh_button = ttk.Button(self.frame, text="Refresh", command=self.update_audio_list)
        self.refresh_button.pack(pady=10)

        # Open Output Folder Button
        self.open_output_button = ttk.Button(self.frame, text="Output Folder", command=self.open_output_folder)
        self.open_output_button.pack(pady=5)

    def update_audio_list(self):
        """
        Update the list of audio files displayed in the listbox.
        """
        self.audio_listbox.delete(0, tk.END)
        output_path = './Output'
        if os.path.exists(output_path):
            try:
                audio_files = [f for f in os.listdir(output_path) if f.endswith('.wav')]
                if self.filter_var.get():
                    audio_files = [f for f in audio_files if f in self.recently_generated]
                for file in audio_files:
                    self.audio_listbox.insert(tk.END, file)
            except Exception as e:
                logger.error(f"Failed to update audio list: {e}")
                messagebox.showerror("Error", f"Failed to update audio list: {e}")
        else:
            logger.warning(f"Output directory does not exist: {output_path}")
            messagebox.showwarning("Warning", f"Output directory does not exist: {output_path}")

    def on_audio_select(self, event):
        """
        Handle the selection of an audio file from the listbox.
        """
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            file_name = event.widget.get(index)
            file_path = os.path.join('./Output', file_name)
            self.load_audio(file_path)

    def load_audio(self, file_path):
        """
        Load an audio file for playback.
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Audio file does not exist: {file_path}")
            pygame.mixer.music.load(file_path)
            self.current_audio = file_path
            self.update_time_label(0, self.get_total_length())
        except Exception as e:
            logger.error(f"Failed to load audio file {file_path}: {e}")
            messagebox.showerror("Error", f"Failed to load audio file: {e}")

    def play(self):
        """
        Play the loaded audio file.
        """
        try:
            if not self.current_audio:
                messagebox.showwarning("Warning", "No audio file selected.")
                return
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play()
                self.update_progress()
            else:
                pygame.mixer.music.unpause()
        except Exception as e:
            logger.error(f"Failed to play audio: {e}")
            messagebox.showerror("Error", f"Failed to play audio: {e}")

    def stop(self):
        """
        Stop audio playback.
        """
        try:
            pygame.mixer.music.stop()
            self.update_time_label(0, self.get_total_length())
        except Exception as e:
            logger.error(f"Failed to stop audio: {e}")
            messagebox.showerror("Error", f"Failed to stop audio: {e}")

    def get_total_length(self):
        """
        Get the total length of the current audio file in milliseconds.
        """
        try:
            if self.current_audio:
                audio = pygame.mixer.Sound(self.current_audio)
                return int(audio.get_length() * 1000)  # In milliseconds
            return 0
        except Exception as e:
            logger.error(f"Failed to get total length of audio: {e}")
            return 0

    def update_time_label(self, current_time, total_time):
        """
        Update the time label showing the current playback position.
        """
        try:
            current_time_s = current_time / 1000.0
            total_time_s = total_time / 1000.0
            self.time_label.config(text=f"{current_time_s:.3f}s / {total_time_s:.3f}s")
        except Exception as e:
            logger.error(f"Failed to update time label: {e}")

    def update_progress(self):
        """
        Continuously update the progress of the audio playback.
        """
        try:
            if pygame.mixer.music.get_busy():
                current_time = pygame.mixer.music.get_pos()  # In milliseconds
                total_time = self.get_total_length()
                self.update_time_label(current_time, total_time)
                # Schedule next update
                self.root.after(100, self.update_progress)
            else:
                # Playback has finished
                self.update_time_label(self.get_total_length(), self.get_total_length())
        except Exception as e:
            logger.error(f"Failed to update progress: {e}")

    def audio_generation_done(self, generated_files):
        """
        Update the list of recently generated audio files.
        """
        self.recently_generated = set(generated_files)
        self.update_audio_list()

    def set_volume(self, volume):
        """
        Set the playback volume.
        """
        try:
            pygame.mixer.music.set_volume(float(volume))
        except Exception as e:
            logger.error(f"Failed to set volume: {e}")
            messagebox.showerror("Error", f"Failed to set volume: {e}")

    def open_output_folder(self):
        """
        Open the output folder in the system's file explorer.
        """
        output_path = './Output'
        if os.path.exists(output_path):
            try:
                subprocess.Popen(f'explorer "{os.path.realpath(output_path)}"', shell=True)
            except Exception as e:
                logger.error(f"Failed to open output folder: {e}")
                messagebox.showerror("Error", f"Failed to open output folder: {e}")
        else:
            logger.warning(f"Output directory does not exist: {output_path}")
            messagebox.showwarning("Warning", f"Output directory does not exist: {output_path}")
