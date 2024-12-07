import torchaudio
import os
import subprocess


def save_audio_file(audio_data, filename, save_path, iteration):
    for i, audio in enumerate(audio_data):
                    file_path = f"{save_path}/{filename}_{iteration}.wav"
                    torchaudio.save(file_path, audio, sample_rate=16000)
                    print(f"Saved audio to {file_path}")