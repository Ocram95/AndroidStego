from loguru import logger
from argparse import ArgumentParser
import os
from utils import check_external_tool_dependencies
import json
import subprocess
import glob
from utils import find_file_path, find_modified_assets

def get_arguments() -> ArgumentParser:
    
    parser = ArgumentParser(description="Reassemble the apk with the stegoassets. Requirements: apktool, apksigner, zipalign and budledecompile")
    parser.add_argument('--decoded_apks', type=str, help="Path to the decoded apks. Default: /mnt/Stegomalware/APK_Stego/decoded/decoded_original")
    args = parser.parse_args()
    
    return args

def main():
    
    args = get_arguments()
    decoded_apks = args.decoded_apks
    if decoded_apks is None:
        decoded_apks = os.path.join('/mnt', 'Stegomalware', 'APK_Stego', 'decoded', 'decoded_original')
    
    statistics_path = os.path.join('..', 'statistics_extractor', 'data')
    for app in os.listdir(decoded_apks):
        oc_seq, oc_sq = find_modified_assets(app, 'OceanLotus')
        lsb_seq, lsb_sq = find_modified_assets(app, 'LSB')
        audio = find_modified_assets(app, 'audio')
    # print(find_file_path(statistics_path, "amazon-shopping", "mshop_alexa_earcon_endpointing.mp3", "audio"))
    


if __name__ == '__main__':
    
    main()