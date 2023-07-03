# Blessing-AI

This python program is made for communicating prompt and result from chatbot interface (e.g oobabooga/text-generation-webui), also able to use MoeGoe TTS, voice recognition or text from User  

![](docs/screenshots/Blessing_AI_Preview.png?raw=true)  

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
- [Credits](#credits)  
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
  
  Locate to [src/Models/models/Voice/](src/Models/Voice/) folder, Create a folder that same name as your character.json file name and put vits model files in the folder.
  
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

:: Location of your Conda Env
call activate "E:\CondaProject\oobaTextGenUI\oobabooga_windows\installer_files\env"

call python server.py --auto-devices --chat --verbose --wbits 4 --groupsize 128 --model_type LLaMA --model pygmalion-7b-4bit-128g-cuda --api

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

- GUI Python Program (WIP)  
  ⚠️ **This method is Working In Progress**: Currently, Text chat only works as input ⚠️  
  Run this command in the [src/](src) folder.  
  
  ```
  python qt_gui_main.py
  ```

### How to use In Program

Wait for loading, when loading is done, program says ```'record ready...'```  
Then, hold 'v' key while speaking through your mic.
If you release the key program detect your voice to text and AI will reply  
Currently, you can only use record while record is ready, I'll update it later that can able to listen your voice any state. (TODO)  

## (Extension) [WIP] Sing request with RVC (Retrieval-based-Voice-Conversion)  
extension for request singing to AI.  
example) user: please sing never gonna give you up! -> send prompt to Language model -> bot: !sing: never gonna give you up -> this program will produce ai covered song with rvc(Retrieval-based-Voice-Conversion)  
### Install RVC-WEBUI  
download the RVC-beta.7z file from here and extract it using 7-Zip into a folder of your choosing. It will take around 4~8GB of space.  
install extra_requirement_rvc  
```
    pip install -r extra_requirement_rvc.txt
```
### Download RVC trained pth files
Download kato megumi pth file from Google drive  
https://drive.google.com/file/d/1mEnR3GXUFGVurQTNauVrJzWC0kEcTmsN/view?usp=sharing (You can use your own pth file)  
extract `kato megumi.zip` copy `kato megumi` folder to Blessing-AI/src/Models/rvc_model
TODO: finish edit

## Credits

This project is built using various open-source libraries and source code. I would like to express my gratitude to the following projects and individuals for their contributions:

### [LanguageLeapAI · GitHub](https://github.com/SociallyIneptWeeb/LanguageLeapAI)
<details>
  <summary>MIT</summary>

    MIT License

    Copyright (c) 2023 bryanlam2001

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

</details>

### [Faster Whisper · GitHub](https://github.com/guillaumekln/faster-whisper)
<details>
  <summary>MIT</summary>

    MIT License

    Copyright (c) 2023 Guillaume Klein

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

</details>

### [MoeGoe · GitHub](https://github.com/CjangCjengh/MoeGoe)
<details>
  <summary>MIT</summary>

    MIT License

    Copyright (c) 2022 CjangCjengh

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

</details>

### [PySide6 · PyPI](https://pypi.org/project/PySide6/)
<details>
  <summary>LGPL</summary>

                           GNU LESSER GENERAL PUBLIC LICENSE
                           Version 3, 29 June 2007

     Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
     Everyone is permitted to copy and distribute verbatim copies
     of this license document, but changing it is not allowed.

      This version of the GNU Lesser General Public License incorporates
    the terms and conditions of version 3 of the GNU General Public
    License, supplemented by the additional permissions listed below.

    0. Additional Definitions.

       As used herein, "this License" refers to version 3 of the GNU Lesser
       General Public License, and the "GNU GPL" refers to version 3 of the GNU
       General Public License.

       "The Library" refers to a covered work governed by this License,
       other than an Application or a Combined Work as defined below.

       An "Application" is any work that makes use of an interface provided
       by the Library, but which is not otherwise based on the Library.
       Defining a subclass of a class defined by the Library is deemed a mode
       of using an interface provided by the Library.

       A "Combined Work" is a work produced by combining or linking an
       Application with the Library.  The particular version of the Library
       with which the Combined Work was made is also called the "Linked
       Version".

       The "Minimal Corresponding Source" for a Combined Work means the
       Corresponding Source for the Combined Work, excluding any source code
       for portions of the Combined Work that, considered in isolation, are
       based on the Application, and not on the Linked Version.

       The "Corresponding Application Code" for a Combined Work means the
       object code and/or source code for the Application, including any data
       and utility programs needed for reproducing the Combined Work from the
       Application, but excluding the System Libraries of the Combined Work.

    1. Exception to Section 3 of the GNU GPL.

       You may convey a covered work under sections 3 and 4 of this License
       without being bound by section 3 of the GNU GPL.

    2. Conveying Modified Versions.

       If you modify a copy of the Library, and, in your modifications, a
       facility refers to a function or data to be supplied by an Application
       that uses the facility (other than as an argument passed when the
       facility is invoked), then you may convey a copy of the modified
       version:

       a) under this License, provided that you make a good faith effort to
       ensure that, in the event an Application does not supply the
       function or data, the facility still operates, and performs
       whatever part of its purpose remains meaningful, or

       b) under the GNU GPL, with none of the additional permissions of
       this License applicable to that copy.

    3. Object Code Incorporating Material from Library Header Files.

       The object code form of an Application may incorporate material from
       a header file that is part of the Library.  You may convey such object
       code under terms of your choice, provided that, if the incorporated
       material is not limited to numerical parameters, data structure
       layouts and accessors, or small macros, inline functions and templates
       (ten or fewer lines in length), you do both of the following:

       a) Give prominent notice with each copy of the object code that the
       Library is used in it and that the Library and its use are
       covered by this License.

       b) Accompany the object code with a copy of the GNU GPL and this license
       document.

    4. Combined Works.

       You may convey a Combined Work under terms of your choice that,
       taken together, effectively do not restrict modification of the
       portions of the Library contained in the Combined Work and reverse
       engineering for debugging such modifications, if you also do each of
       the following:

       a) Give prominent notice with each copy of the Combined Work that
       the Library is used in it and that the Library and its use are
       covered by this License.

       b) Accompany the Combined Work with a copy of the GNU GPL and this license
       document.

       c) For a Combined Work that displays copyright notices during
       execution, include the copyright notice for the Library among
       these notices, as well as a reference directing the user to the
       copies of the GNU GPL and this license document.

       d) Do one of the following:

       0) Convey the Minimal Corresponding Source under the terms of this
          License, and the Corresponding Application Code in a form
          suitable for, and under terms that permit, the user to
          recombine or relink the Application with a modified version of
          the Linked Version to produce a modified Combined Work, in the
          manner specified by section 6 of the GNU GPL for conveying
          Corresponding Source.

       1) Use a suitable shared library mechanism for linking with the
          Library.  A suitable mechanism is one that (a) uses at run time
          a copy of the Library already present on the user's computer
          system, and (b) will operate properly with a modified version
          of the Library that is interface-compatible with the Linked
          Version.

       e) Provide Installation Information, but only if you would otherwise
       be required to provide such information under section 6 of the
       GNU GPL, and only to the extent that such information is
       necessary to install and execute a modified version of the
       Combined Work produced by recombining or relinking the
       Application with a modified version of the Linked Version. (If
       you use option 4d0, the Installation Information must accompany
       the Minimal Corresponding Source and Corresponding Application
       Code. If you use option 4d1, you must provide the Installation
       Information in the manner specified by section 6 of the GNU GPL
       for conveying Corresponding Source.)

    5. Combined Libraries.

       You may place library facilities that are a work based on the
       Library side by side in a single library together with other library
       facilities that are not Applications and are not covered by this
       License, and convey such a combined library under terms of your
       choice, if you do both of the following:

       a) Accompany the combined library with a copy of the same work based
       on the Library, uncombined with any other library facilities,
       conveyed under the terms of this License.

       b) Give prominent notice with the combined library that part of it
       is a work based on the Library, and explaining where to find the
       accompanying uncombined form of the same work.

    6. Revised Versions of the GNU Lesser General Public License.

       The Free Software Foundation may publish revised and/or new versions
       of the GNU Lesser General Public License from time to time. Such new
       versions will be similar in spirit to the present version, but may
       differ in detail to address new problems or concerns.

       Each version is given a distinguishing version number. If the
       Library as you received it specifies that a certain numbered version
       of the GNU Lesser General Public License "or any later version"
       applies to it, you have the option of following the terms and
       conditions either of that published version or of any later version
       published by the Free Software Foundation. If the Library as you
       received it does not specify a version number of the GNU Lesser
       General Public License, you may choose any version of the GNU Lesser
       General Public License ever published by the Free Software Foundation.

       If the Library as you received it specifies that a proxy can decide
       whether future versions of the GNU Lesser General Public License shall
       apply, that proxy's public statement of acceptance of any version is
       permanent authorization for you to choose that version for the
       Library.

</details>

### (GUI Templates) [PyDracula · GitHub](https://github.com/Wanderson-Magalhaes/Modern_GUI_PyDracula_PySide6_or_PyQt6) | [PyBlackBox · GitHub](https://github.com/Wanderson-Magalhaes/PyBlackBox_Qt_Widgets_PySide6_Or_PyQt6_v1.0.0)
<details>
  <summary>MIT</summary>

    MIT License

    Copyright (c) 2021 Wanderson M. Pimenta

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

</details>

## License

The code of BlessingAI is released under the MIT License. See [LICENSE](LICENSE.md) for further details.


