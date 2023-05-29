# Writing your .env file

First, copy [.env.sample](../.env.sample) to .env by running the following command.

```cp .env.sample .env```

Now open .env in a text editor of your choice and update the variables. Below is a more detailed description of each environment variable

## Logging

This variable can be set to either _True_ or _False_. Set to _True_ if you would like to see more detailed logging from the terminal when running the python scripts.  
Set to _False_ if you want to disable logging.

## TextGen API Url

If you run Language Model Interface (oobabooga/text-generation-webui) In Local,  
<span style="color: red;">TEXTGENERATION_URL = </span> http://localhost:5000

In Cloud,  
<span style="color: red;">TEXTGENERATION_URL = </span>[ <u>your_public_Url</u>](screenshots/ColabApiServerUrl.png)

## Papago Translator Key

**If there's no Papago Auth ID and Secret, program will try to translate using Google Translator**  

this program is using NaverPapago translotor. more Information is here (https://developers.naver.com/products/papago/nmt/nmt.md)  
put Client ID to PAPAGO_AUTH_ID, Client Secret to PAPAGO_AUTH_SECRET  

if you want to change translator to other, change definition of method `DoTranslate()` in `voice_translator.py`  

## Discord Bot Key (optional)

if you want to use discord bot, 1.create a new Webhook 2. put webhook_token and channel_id of your server's text-channel

## Push to talk key

The key to hold down when you want your voice to be recorded and translated. E.g. MIC_RECORD_KEY=t if you want to hold down the 't' key.

## Audio Device Ids

I will change the code that automatically detect user's device if there's nothing set (TODO)

Here is where you will enter the IDs for the various audio devices that the program will be using.  
This is required for python to know which audio device to listen from or play audio to.  
Run [get_audio_device_ids.py](../src/modules/get_audio_device_ids.py) in order to obtain the id for your audio devices.  
The output from running this command may be truncated but do your best to select the correct id for the audio device.  

## Target Language code

Here is what language will be spoken by TTS program.  
`TARGET_LANGUAGE_CODE=ja` - `ja` is default  
Also it supports korean. just replace `ja` to `ko`  
`en` is not supported yet, I'll update it later...  

## Edit Voice Settings file

At root folder (Blessing-AI/), You can find ***Voice_settings.txt***. You can change the settings through it while program is running.

program will load this text file as json so Do not destroy the structure.

```
"discord_bot": false,         <- use discord bot?
"max_token": 200,            <- max tokens for bot's reply
"voice_id": 0,                      <- moegoe_config's voice id (set it 0, if you're not sure)
"voice_speed": 0.8,                         <- TTS voice speed
"voice_volume": 0.3,                       <- TTS voice volume
"intonation_scale": 1.5,                  <-unused
"pre_phoneme_length": 1.0,         <-unused
"post_phoneme_length": 1.0        <-unused
```

<!-- ## Voicevox Settings

Choose which speaker to use from Voicevox by updating VOICE_ID. 
Send a curl request to get a list of all speaker IDs and their corresponding speakers.
Replace <VOICEVOX_BASE_URL> with the url that Voicevox is hosted at.

```curl <VOICEVOX_BASE_URL>/speakers```

Feel free to adjust the scaling of the speaker's volume, speed or intonation as well.

## Subtitle Settings

RECORD_TIMEOUT is the max number of seconds for [Audio Subtitler](../src/subtitler.py) to listen for before passing the audio to Whisper.

PHRASE_TIMEOUT is the max number of seconds between subtitles before starting a new one.

REQUEST_TIMEOUT is the max number of seconds to wait for a translation response from Whisper before dropping the request.
This is useful if you do not want old subtitles that took too long to process to overwrite current ones.

OFFSET_X and OFFSET_Y is the number of pixels from the bottom middle of the screen for subtitles to be displayed.

SUBTITLE_FONT_SIZE and SUBTITLE_COLOR is self explanatory.

SUBTITLE_BG_COLOR is the background color of your subtitles

SACRIFICIAL_COLOR is the color that will be considered transparent. This is for the subtitles to appear without python's tkinter window showing up and blocking the screen.

SACRIFICIAL_COLOR can be set to the same color as SUBTITLE_BG_COLOR so that subtitles will not have a background color.
SUBTITLE_COLOR shouldn't be set to the same color as SACRIFICIAL_COLOR as this will cause your subtitles to be invisible.
 -->

## Finish

You are finally done setting up your environment variables. To start running **Blessing AI**, go to [usage](../README.md#Usage).
