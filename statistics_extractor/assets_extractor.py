from info_extractor import get_arguments, find_files, apkdecode
import os
import glob
from typing import Dict


def find_files(decoded_apks: str) -> Dict:
    """
    Find files by extension

    Parameters
    ----------
    decoded_apks : str
        path of the decoded apks

    Returns
    -------
    Dict
        dict with one list for every file type
    """
    files = {app: {'images': list(), 'audio': list(), 'video': list()} for app in os.listdir(decoded_apks)}
    print(files)
    for app in os.listdir(decoded_apks):
        print(f'[+] Finding files for {app}')
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.gif']:
            files[app]['images'] += glob(os.path.join(decoded_apks, app, 'res', '*', ext))
        for ext in ['*.mp4']:
            files[app]['video'] += glob(os.path.join(decoded_apks, app, 'res', '*', ext))
        for ext in ['*.mp3', '*.wav', '*.flac']:
            files[app]['audio'] += glob(os.path.join(decoded_apks, app, 'res', '*', ext))
        break
    return files
    

def main():
    args = get_arguments()
    decode = args.decode
    input_apks = args.input_apks
    if input_apks is None:
        input_apks = os.path.join('/mnt', 'Stegomalware', 'APK_Stego')
    
    if decode:
        apkdecode(input_apks)
    
    files = find_files(os.path.join(input_apks, 'decoded'))
    print(files)


if __name__ == '__main__':
    main()
