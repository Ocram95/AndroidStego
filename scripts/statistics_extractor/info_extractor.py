import os
from MediaExtractor import MediaExtractor
from loguru import logger
from glob import glob
from typing import Dict
from json import dump
from pandas import DataFrame
from StatisticsExtractor import StatisticsExtractor
import numpy as np
from utils import get_arguments, NpEncoder, apkdecode, check_resolution
    

def find_files(decoded_apks: str, done: list) -> Dict:
    """
    Find files by extension

    Parameters
    ----------
    decoded_apks : str
        path of the decoded apks
    done: list
        done apks not to parse

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
        if app in done:
            continue
        print(f'[+] Finding files for {app}')
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.gif']:
            files['images'] += glob(os.path.join(decoded_apks, app, 'res', '*', ext))
        for ext in ['*.mp4']:
            files['video'] += glob(os.path.join(decoded_apks, app, 'res', '*', ext))
        for ext in ['*.mp3', '*.wav', '*.flac']:
            files['audio'] += glob(os.path.join(decoded_apks, app, 'res', '*', ext))
        
    return files

def find_files_per_app(decoded_apks: str, done: list) -> Dict:
    """
    Find files by extension

    Parameters
    ----------
    decoded_apks : str
        path of the decoded apks
    done: list
        done apks not to parse

    Returns
    -------
    Dict
        dict with one list for every file type
    """
    files = {app: {'images': list(), 'audio': list(), 'video': list()} for app in os.listdir(decoded_apks)}
    
    for app in os.listdir(decoded_apks):
        if app in done:
            continue
        print(f'[+] Finding files for {app}')
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.gif']:
            files[app]['images'] += glob(os.path.join(decoded_apks, app, 'res', '*', ext))
        for ext in ['*.mp4']:
            files[app]['video'] += glob(os.path.join(decoded_apks, app, 'res', '*', ext))
        for ext in ['*.mp3', '*.wav', '*.flac']:
            files[app]['audio'] += glob(os.path.join(decoded_apks, app, 'res', '*', ext))

    return files
    

def main():
    
    args = get_arguments()
    decode = args.decode
    input_apks = args.input_apks
    statistics = args.statistics
    if input_apks is None:
        input_apks = os.path.join('/mnt', 'Stegomalware', 'APK_Stego')
    
    done = [d for d in os.listdir(os.path.join(input_apks, 'decoded', 'decoded_original'))]
    
    if decode:
        apkdecode(input_apks, done)

    if statistics:
        files = find_files(os.path.join(input_apks, 'decoded', 'decoded_original'))
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
    
    else:
        # write info about each asset in json files
        files = find_files_per_app(os.path.join(input_apks, 'decoded'))
        for k, v in files.items():
            print(f'[+] Extracting info for {k}')
            logger.info(f'[+] Extracting info for {k}')
            images = list()
            audio = list()
            video = list()
            for k1, v1 in v.items():
                for f in v1:
                    extractor = MediaExtractor(f)
                    extracted_info = extractor.extract_info()
                    if extracted_info is None:
                        continue
                    if k1 == 'images':
                        if check_resolution(extracted_info['info']['width'], extracted_info['info']['height']):
                            images.append(extracted_info)
                    elif k1 == 'audio':
                        audio.append(extracted_info)
                    elif k1 == 'video':
                        video.append(extracted_info)
            p = k.replace('_', '')
            if len(images) != 0:
                with open(os.path.join('./data', f'{p}_images.json'), 'w') as fp:
                    dump(images, fp, cls=NpEncoder, indent=4)
            if len(audio) != 0:
                with open(os.path.join('./data', f'{p}_audio.json'), 'w') as fp:
                    dump(audio, fp, cls=NpEncoder, indent=4)
            if len(video) != 0:
                with open(os.path.join('./data', f'{p}_video.json'), 'w') as fp:
                    dump(video, fp, cls=NpEncoder, indent=4)
            
            
if __name__ == '__main__':
    logger.remove()
    logger.add("info_extractor.log", format='{message}', level="INFO")
    main()