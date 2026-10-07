# Vibrotactile Audio Generator

*Vous cherchez la version originale française ? Elle reste disponible [ici](./README.fr.md).*

The Vibrotactile Audio Generator is an advanced Python application to generate and play audio files imitating tactile sensations. This tool is made for developers and researchers working on projects related to vibrotactile haptic feedback, particularly video games and exteneded reality (XR) applications.

## Features

- **Audio Generation**: A large language model (LLM) is used to produce detailed vibrotactile descriptions and AudioCraft is used to generate the corresponding audio files.
- **Advanced Mode**: This mode allows users to give feedback to modify an LLM's response in order to generate the audio files.
- **Audio Playback**: Generated files can be played back using the integrated media player in the app.
- **Customizable Settings**: Modify the parameters of the LLM, the path where files are saved, and options related to the vibrotactile audio generation.
- **File Management**: Browse and easily manage the generated audio files.

## How it works

1. **Enter a description**: Write a description of a desired tactile sensation.
2. **Generate a detailed description**: The LLM generates a detailed description of the vibrotactile haptic feedback.
3. **Create the sound**: AudioCraft transforms the LLM-generated description into an audio file.
4. **Review and adjust**: Use the advanced mode in order to iteratively modify the effect.
5. **Play and Compare**: Play back the generated vibrotactile audio files directly in the application.

## Configuration

The `config.py` file contains the following customizable settings:
- `model_name`: Specify the LLM model to use.
- `api_url`: The base URL of the LLM API (OpenAI by default, an Ollama version is present in a dedicated branch).
- `temperature`: Control the variability of the LLM responses (higher value = more variability).
- `default_save_path`: The path to save to the generated audio files.
- `advanced_mode_enabled`: Whether Advanced Mode should be enabled on startup.

Modify the parameters to your preferences prior to starting the application.

## File structure

Here is an overview of the structure of the project:

- **`main.py`**: Entry point of the application.
- **`gui.py`**: Defines the graphical user interface.
- **`logic.py`**: Calls AudioCraft to generate the audio files from a description.
- **`audio_player.py`**: Handles audio playback.
- **`llm.py`**: Generates the vibrotactile descriptions using a large language model (LLM).
- **`utils.py`**: Utility functions to save and manage the audio files.
- **`config.py`**: Configuration file for application settings.

### Dependency Installation

To run the program, follow these steps:

1. **Install Python 3.10**
  The program has been tested using Python 3.10 since it was not possible to get AudioCraft running with other versions. If you can get AudioCraft to work with another, more recent Python version, you can use it without a problem.
  You can download Python 3.10 from [python.org](https://www.python.org/).

2. **Install AudioCraft and its dependencies**
AudioCraft is used to generate the audio files. Follow the instructions provided in the official AudioCraft repository:
[Install AudioCraft](https://github.com/facebookresearch/audiocraft/tree/main).

Here are the instructions that they provide:
AudioCraft requires Python 3.9, PyTorch 2.1.0. To install AudioCraft, you can run the following:
```
# Best to make sure you have torch installed first, in particular before installing xformers.
# Don't run this if you already have PyTorch installed.
python -m pip install 'torch==2.1.0'
# You might need the following before trying to install the packages
python -m pip install setuptools wheel
# Then proceed to one of the following
python -m pip install -U audiocraft  # stable release
python -m pip install -U git+https://git@github.com/facebookresearch/audiocraft#egg=audiocraft  # bleeding edge
python -m pip install -e .  # or if you cloned the repo locally (mandatory if you want to train).
python -m pip install -e '.[wm]'  # if you want to train a watermarking model
```

We also recommend having ffmpeg installed, either through your system or Anaconda:
```
sudo apt-get install ffmpeg
# Or if you are using Anaconda or Miniconda
conda install "ffmpeg<5" -c conda-forge
```

3. **Install LangChain and LangChain OpenAI**
LangChain is used to handle interactions with the large language models. Install LangChain and LangChain OpenAI with the following command:
```
pip install langchain langchain-openai
```
Note: If the program is modified to use another LLM API, another LangChain package may be necessary (e.g., `langchain-ollama` for calling LLMs via Ollama).

4. **Install `pygame` for audio playback**
Use the following command to install `pygame`:
```
pip install pygame
```

5. **Verify that Tkinter is installed**
Tkinter is used for the graphical user interface and is generally included by default with Python. If this is not the case, install it via your system's package manager:
- On **Ubuntu/Linux**:
  ```
  sudo apt-get install python3-tk
  ```
- On **Windows/MacOS**, Tkinter is included with the standard Python installation.

6. **Test the installation**
Once all the dependencies are installed, run the program to verify it works correctly:
```
python main.py
```

### Comments

- **Python 3.10** is recommended due to AudioCraft not working with other versions during testing. If you make it work with a more recent Python version, that verson of Python can be used.
- Take care to closely following the installation instructions for AudioCraft as it also installs important dependencies such as PyTorch and TorchAudio.

If you encounter problems, verify that all of the above steps have been followed correctly and that your libraries are up to date.

## Usage
For more detailed information on how this project works, please consult the [Documentation (French only)](./DOCUMENTATION.md).

### Normal Mode
1. Open the application and enter a description of a vibrotactile sensation in the input field.
2. Click on "Generate" to generate a description and create an audio file.
3. Playback the file in the **Audio Playback** tab.

### Advanced Mode
1. Check the **Advanced Mode** option in the **Audio Generation** tab.
2. Modify and refine the LLM responses iteratively.
3. generate the audio after finalizing the descriptions in the responses.

### Playback and Management
- Use the tab **Audio Playback** to play the audio files.
- Open the output folder to manage the generated files.

## Technologies Used

- **Python**: Main programming language
- **Tkinter**: GUI framework for creating multiplatform interfaces
- **LangChain**: Generates vibrotactile descriptions via the LLM
- **AudioCraft**: Transforms a written description into an audio file.
- **PyGame**: Audio playback support
- **TorchAudio**: For saving and loading audio files.
