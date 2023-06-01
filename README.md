# Blessing-AI

This python program is made for communicating prompt and result from chatbot interface (e.g oobabooga/text-generation-webui), also able to use MoeGoe TTS, voice recognition or text from User

***Note: This project is a work in progress.***  
Please note that this project is currently under development and may not be feature-complete or stable. Use it at your own risk, and feel free to contribute or provide feedback. We appreciate your understanding and patience as we continue to improve and enhance the project.

## Table of Contents

- [Installation](#installation-windows)  
- [Setting Env](#setting-env-file)  
- [Install Language Model/Interface](#install-language-model--interface)  
  - [In Cloud](#1-run-text-gen-on-cloud-optional)  
  - [In Local](#1-install-languagemodel-interface-local)  
- [Usage](#usage)  
  - [1. Run Language Model Interface](#1-run-language-model-interface-local)  
  - [2. Run Blessing AI](#2-run-blessing-ai-3-options)  
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

- Currently I'm using an Anime Character 'Kato Megumi' VITS model from 'Saekano' (CV: Kiyono Yasuno (安野 希世乃))  
  To download this model https://drive.google.com/file/d/1Qcr6OpnuZGc3Vw54kdV8-k9TTijiDTsF/view?usp=share_link  
  In zip file there are 2 files (G_latest.pth, moegoe_config.json).  
  
  Locate to [src/Models/models/Voice/](src/Models/Voice/) folder, Create a folder that same name as your character.json file name.  and paste vits model files in the folder.
  
  for example, if you have a `Kato Megumi.json` character file in  [src/Models/models/Characters/](src/Models/Characters/) folder, then create a folder `Kato Megumi`in Voice folder and paste `G_latest.pth`,`moegoe_config.json` files In the created folder.

  ![](docs/screenshots/MoeGoeModels.png?raw=true)

## Setting Env file

 :warning: **If you don't do setting your env file, program won't work)** :warning:  
This env is setting file contains Translator API key, Audio device ID, keyboard key settings. as Default, these settings are blank. so you should insert them following under document.  
go to [Env](docs/ENV.md) Document.  

## Install Language Model / Interface

### 1. Run Text-Gen on Cloud (Optional)

:pushpin: **If you don't have a decent GPU and trying to run this on Cloud, Try this Option.  
Also You don't need to follow (Local) steps below**  

- Using Google Colab, you can able to manage Large Language models has 13B parameters  
  ([Google Colab Link](https://colab.research.google.com/drive/1VwEONZNajP4WGwJ8bw55MODHQ_yq1hpJ?usp=sharing))
  ![](docs/screenshots/ColabApiServerUrl.png?raw=true)
  
  In .env setting file, Copy and Paste the Url to  
  
  ```diff
  TEXTGENERATION_URL =                #Paste Url Here (no need to add Quotation mark)
  ```
  
  Check more information in [Env](https://github.com/HWcomss/Blessing-AI/blob/main/docs/ENV.md#textgen-api-url) document  
  
  Also if you want to use other Cloud services or Language models, Check [this video](https://www.youtube.com/watch?v=TP2yID7Ubr4&t=2s) by Aitrepreneur

### 1. Install LanguageModel Interface (Local)

To generate prompt from user's input(voice) and get result, **I'm using oobabooga/text-generation-webui**  

- Please follow the installation from here  
  https://github.com/oobabooga/text-generation-webui#installation  

### 2. Download Language Model (local)

- Download any Language Model. I'm using Pygmlion-7b-4bit model  
  https://github.com/oobabooga/text-generation-webui#downloading-models  
  follow the installation above, Hugging face Link of the Pygmalion model is here  
  https://huggingface.co/TehVenom/Pygmalion-7b-4bit-Q4_1-GGML  

## Usage

**If you are running Text Genartion Web UI On Google colab, Skip to [2. Run Blessing-AI](#2-run-blessing-ai-3-options)**  

### 1. Run Language Model Interface (Local)

Go to oobabooga/text-generation-webui folder installed, open cmd at current folder
use below commands that you can run Interface while activate conda, please see this as reference. - https://github.com/oobabooga/text-generation-webui#starting-the-web-ui  

```
conda activate textgen
cd text-generation-webui
python server.py --api
```

Please load your language model and character from webUI  
Or add start options at behind where `python server.py --api`. --api is necessary because of Blessing-AI is using it.
more information here (https://github.com/oobabooga/text-generation-webui#basic-settings)  

If you want to make batch file here's my example **(optional)**  

```
::start-webui.bat
@echo off

@echo Starting the web UI...

call activate "E:\CondaProject\oobaTextGenUI\oobabooga_windows\installer_files\env" <- Location of your Conda Env

call python server.py --auto-devices --chat --verbose --wbits 4 --groupsize 128 --model_type LLaMA --model pygmalion-7b-4bit-128g-cuda --character "Kato Megumi" --api

pause
```

### 2. Run Blessing-AI (3 options)

- Run as executable file (recommended)  
  run ```AIVoice.exe```

- Run as Batch file  
  run ```Start.bat```

- Python Program
  Run this command in the [src/](src) folder.  
  
  ```
  python voice_translator.py
  ```

### How to use In Program

Wait for loading, when loading is done, program says ```'record ready...'```  
Then, hold 'v' key while speaking through your mic.
If you release the key program detect your voice to text and AI will reply  
currently, it won't working because there's no character's information and ChatLog file In this repository. but will be fix In future (TODO)
Currently, you can only use record while record is ready, I'll update it later that can able to listen your voice any state. (TODO)  

## License

The code of BlessingAI is released under the MIT License. See [LICENSE](LICENSE.md) for further details.
