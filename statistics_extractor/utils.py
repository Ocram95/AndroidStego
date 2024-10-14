from json import dump, JSONEncoder
from argparse import ArgumentParser
import numpy as np
import os
import subprocess

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
    parser.add_argument("--statistics", action="store_true", help="Whether or not to extract statistics")
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


def check_resolution(width: int, height: int) -> bool:
    """_summary_

    Parameters
    ----------
    width : int
        _description_
    height : int
        _description_

    Returns
    -------
    bool
        _description_
    """
    
    return (width, height) == (72, 72) or (width, height) == (48, 48) or (width, height) == (32, 32)