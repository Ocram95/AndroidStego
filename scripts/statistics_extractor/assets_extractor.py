from info_extractor import get_arguments, find_files, apkdecode
import os
import glob
from typing import Dict
from json import load
from shutil import make_archive, copy, rmtree
    

def main():
    
    data = os.path.join('./data')
    data_files = list(set(glob.glob(os.path.join(data, '*_*.json'))) - set(glob.glob(os.path.join(data, 'stats_*.json'))))
    
    for data in data_files:
        with open(data, 'r') as fp:
            data_loaded = load(fp)
        path = os.path.join('/mnt', 'Stegomalware', 'APK_Stego', 'assets', data.split('/')[2].split('_')[0])
        if not os.path.exists(path):
            os.mkdir(path)
        path1 = os.path.join(path, data.split('/')[2].split('_')[1].split('.')[0])
        if not os.path.exists(path1):
            os.mkdir(path1)
        found72, found48, found32, foundjpg = False, False, False, False
        found = 0

        for i, file in enumerate(data_loaded):

            if not found72 and data.split('/')[2].split('_')[1].split('.')[0] == 'images' and (file['info']['width'], file['info']['width']) == (72, 72) and found < 2:
                copy(file['file'], path1)
                found72 = True
                found = found + 1
            if not found48 and data.split('/')[2].split('_')[1].split('.')[0] == 'images' and (file['info']['width'], file['info']['width']) == (48, 48) and found < 2:
                copy(file['file'], path1)
                found48 = True
                found = found + 1
            if not found32 and data.split('/')[2].split('_')[1].split('.')[0] == 'images' and (file['info']['width'], file['info']['width']) == (32, 32) and found < 2:
                copy(file['file'], path1)
                found48 = True
                found = found + 1
            if not foundjpg and data.split('/')[2].split('_')[1].split('.')[0] == 'images' and file['type'] == 'jpg' or file['type'] == 'jpeg' and found < 2:
                copy(file['file'], path1)
                foundjpg = True
                found = found + 1
            if data.split('/')[2].split('_')[1].split('.')[0] != 'images' and found < 2:
                copy(file['file'], path1)
                found = found + 1

                

if __name__ == '__main__':
    main()
