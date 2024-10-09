import os
import subprocess
from MediaExtractor import MediaExtractor
from argparse import ArgumentParser
from loguru import logger
from glob import glob
from typing import Dict
from json import dump, JSONEncoder
from pandas import DataFrame
from StatisticsExtractor import StatisticsExtractor
import numpy as np

class NpEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.int64):
            return int(obj)
        if isinstance(obj, float):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.uint8):
            return int(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super(NpEncoder, self).default(obj)

def get_arguments() -> ArgumentParser:
    
    parser = ArgumentParser(description="")
    parser.add_argument("--decode", action="store_true", help="Whether or not to decode apks")
    parser.add_argument('--input_apks', type=str, help="Path to input apks. Default: /mnt/Stegomalware/APK_Stego/")
    args = parser.parse_args()
    
    return args

def apkdecode(input_apks: str):
    """
    Decode apk in input_apks folder

    Parameters
    -------
    input_apks: str
        path of the apks to decode
    """
    for app in os.listdir(os.path.join(input_apks, 'apk')):
        name = app.split('.')[0]
        if not os.path.exists(os.path.join(input_apks, 'decoded', name)):
            print(f"[+] Decoding {name}")
            if 'apkm' in app:
                subprocess.run(f"""
                                apktool d {os.path.join(input_apks, 'apk', app)} --output {os.path.join(input_apks, 'decoded', name)} &&
                                apktool d {os.path.join(input_apks, 'decoded', name, 'unknown', 'base.apk')} --output {os.path.join(input_apks, 'decoded', 'base_'+name)} &&
                                rm -rf {os.path.join(input_apks, 'decoded', name)} && 
                                mv {os.path.join(input_apks, 'decoded', 'base_'+name)} {os.path.join(input_apks, 'decoded', name)}
                                """, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                subprocess.run(f"apktool d {os.path.join(input_apks, 'apk', app)} --output {os.path.join(input_apks, 'decoded', name)}", shell=True, 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    

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
    files = {
        'images': list(),
        'audio': list(),
        'video': list()
    }
    
    for app in os.listdir(decoded_apks):
        print(f'[+] Finding files for {app}')
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.gif']:
            files['images'] += glob(os.path.join(decoded_apks, app, 'res', '*', ext))
        for ext in ['*.mp4']:
            files['video'] += glob(os.path.join(decoded_apks, app, 'res', '*', ext))
        for ext in ['*.mp3', '*.wav', '*.flac']:
            files['audio'] += glob(os.path.join(decoded_apks, app, 'res', '*', ext))
        
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

    info = {
        'images': {'jpg': [], 'gif': [], 'jpeg': [], 'png': [], 'bmp': []},
        'audio': {'mp3': [], 'wav': []},
        'video': {'mp4': []}
    }
    for k, v in files.items():
        print(f'[+] Extracting info for {k}')
        for f in v:
            extractor = MediaExtractor(f)
            extracted_info = extractor.extract_info()
            if extracted_info is None:
                continue
            info[k][extracted_info['type']].append(extracted_info['info'])
    
    statistics = {
                'images': {'jpg': [], 'gif': [], 'jpeg': [], 'png': [], 'bmp': []},
                'audio': {'mp3': [], 'wav': []},
                'video': {'mp4': []}
    }
    
    for k, v in info.items():
        print(f'[+] Extracting statistics for {k}')
        for k1, v1 in v.items():
            if len(v1) != 0:
                statistics_extractor = StatisticsExtractor(DataFrame(v1), k)
                statistics[k][k1] = statistics_extractor.compute_statistics()
    
    with open('stats_img.json', 'w') as fp:
        dump(statistics['images'], fp, cls=NpEncoder, indent=4)
    
    with open('stats_audio.json', 'w') as fp:
        dump(statistics['audio'], fp, cls=NpEncoder, indent=4)
    
    with open('stats_video.json', 'w') as fp:
        dump(statistics['video'], fp, cls=NpEncoder, indent=4)
            
            
if __name__ == '__main__':
    logger.remove()
    logger.add("info_extractor.log", format='{message}', level="INFO")
    main()