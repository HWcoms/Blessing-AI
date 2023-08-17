from pathlib import Path
import requests
import os

MDX_DOWNLOAD_LINK = 'https://github.com/TRvlvr/model_repo/releases/download/all_public_uvr_models/'
RVC_DOWNLOAD_LINK = 'https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/'

BASE_DIR = Path(__file__).resolve().parent.parent.parent
BASE_DIR = os.path.join(BASE_DIR, 'Models', 'rvc_model')

logging = True

# CHECK BASE_DIR
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)
    print("\033[34m" + f"[download_rvc_models]: Created Base folder! \033[33m[{BASE_DIR}]" + "\033[0m")


def check_files(model_name, dir_name):
    full_path = os.path.join(dir_name, model_name)
    if os.path.exists(full_path):
        return True
    return False


def mod_print(str_to_print):
    if logging:
        print(str_to_print)


def dl_model(link, model_name, dir_name):
    with requests.get(f'{link}{model_name}') as r:
        r.raise_for_status()
        with open(os.path.join(dir_name, model_name), 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


def download_required_models():
    _mdx_model_names = ['UVR-MDX-NET-Voc_FT.onnx', 'UVR_MDXNET_KARA_2.onnx', 'Reverb_HQ_By_FoxJoy.onnx']
    for _model in _mdx_model_names:
        if not check_files(_model, BASE_DIR):
            mod_print(f'Downloading {_model}...')
            dl_model(MDX_DOWNLOAD_LINK, _model, BASE_DIR)
        # else:
        #     mod_print(f'{_model} Found...')

    _rvc_model_names = ['hubert_base.pt', 'rmvpe.pt']
    for _model in _rvc_model_names:
        if not check_files(_model, BASE_DIR):
            mod_print(f'Downloading {_model}...')
            dl_model(RVC_DOWNLOAD_LINK, _model, BASE_DIR)
        # else:
        #     mod_print(f'{_model} Found...')

    mod_print(f'All RVC required models are downloaded! : {_mdx_model_names} + {_rvc_model_names}')


if __name__ == '__main__':
    mdx_model_names = ['UVR-MDX-NET-Voc_FT.onnx', 'UVR_MDXNET_KARA_2.onnx', 'Reverb_HQ_By_FoxJoy.onnx']
    for model in mdx_model_names:
        if not check_files(model, BASE_DIR):
            mod_print(f'Downloading {model}...')
            dl_model(MDX_DOWNLOAD_LINK, model, BASE_DIR)
        else:
            mod_print(f'{model} Found...')

    rvc_model_names = ['hubert_base.pt', 'rmvpe.pt']
    for model in rvc_model_names:
        if not check_files(model, BASE_DIR):
            mod_print(f'Downloading {model}...')
            dl_model(RVC_DOWNLOAD_LINK, model, BASE_DIR)
        else:
            mod_print(f'{model} Found...')

    mod_print('All RVC required models are downloaded!')
