# Blessing-AI
this python program is made for communicating prompt and result from chatbot interface (e.g oobabooga/text-generation-webui), also able to use MoeGoe TTS, voice recognition or text from User

***Note: This project is a work in progress.***  
Please note that this project is currently under development and may not be feature-complete or stable. Use it at your own risk, and feel free to contribute or provide feedback. We appreciate your understanding and patience as we continue to improve and enhance the project.

## Table of Contents

- [Installation](#installation-windows) 
- [Setting Env](#setting-env-file)
- [Usage](#usage)
  - [How to use](#how-to-use-in-program)
- [License](#license)

## Installation (Windows)
I only tested on this specific versions but I didn't test it on others so please install same version as possible  
also **please consider using conda to avoid version conflicts**  
I'm using Python 3.10.6 (https://www.python.org/downloads/release/python-3106/)  

- Cloning this repository
  - Run this command to clone this entire repository.
    ```
    git clone https://github.com/HWcomss/Blessing-AI
    ```
  - Navigate to the cloned repository
    ```
    cd Blessing-AI
    ```
  - Run the following command in the root folder to install the required python dependencies.
    ```
    pip install -r requirements.txt
    ```
  - Install pyTorch from this site (https://pytorch.org/get-started/locally/)  
  e.g ```pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118``` **I only tested on CUDA 11.8**

- Download MoeGoe character model (MoeGoe TTS model)
  - You can use other model if you want other voice (need 2files - G_latest.pth, moegoe_config.json) (optional)  


  - currently I'm using fine-tuned Kamisato Ayaka voice model from Genshin Impact (CV: Hayami Saori (早見 沙織))  
    To download this model https://drive.google.com/file/d/1maqIWA04nl8SAbsuLiNRPtnaX2WpOY0D/view?usp=sharing  
    In zip file there are 2 files (G_latest.pth, moegoe_config.json). Paste these files in [src/MoeGoe/models](src/MoeGoe/models) folder  
    
    ![](docs/screenshots/MoeGoeModels.png?raw=true)
     
## Setting Env file
**if you don't do setting your env file, program won't work)**  
this env is setting file contains Translator API key, Audio device ID, keyboard key settings. as Default, these settings are blank. so you should insert them following under document.  
go to [Env](docs/ENV.md) Document.  

## Usage

### Run as Executable file (recommended)
run ```AIVoice.exe```

### Run as Batch file
run ```Start.bat```

### Python Program
Run this command in the [src/](src) folder.
```
python voice_translator.py
```

### How to use In Program

Wait for loading, when loading is done, program says ```'record ready...'```  
then, hold 'v' key while speaking through your mic.
if you release the key program detect your voice to text and AI will speak in Japanese(Translate with Naver Papago API) what you said - I'll use Language model to make chatbot AI later (TODO)  
currently, you can only use record while record is ready, I'll update it later that can able to listen your voice any state. (TODO)  

## License

The code of BlessingAI is released under the MIT License. See [LICENSE](LICENSE.md) for further details.
