from tool import Apktool, ApkSigner, Zipalign
from toolbundledecompiler import BundleDecompiler
from loguru import logger
import subprocess
import os
import glob
from hashlib import sha256
import json
from itertools import combinations
from loguru import logger
import config
import random
import string

def combine(elements: list) -> list:
        
        all_combintations = list()
        for length in range(1, len(elements)+1):
            all_combintations.extend(combinations(elements, length))
        
        return all_combintations

def check_external_tool_dependencies():
    """
    Make sure all the external needed tools are available and ready to be used.
    """
    # APKTOOL_PATH, APKSIGNER_PATH and ZIPALIGN_PATH environment variables can be
    # used to specify the location of the external tools (make sure they have the
    # execute permission). If there is a problem with any of the executables below,
    # an exception will be thrown by the corresponding constructor.
    logger.debug("Checking external tool dependencies")
    Apktool()
    BundleDecompiler()
    ApkSigner()
    Zipalign()


def find_file_path(statistics_path: str, app: str, asset_name:str, type:str)->str:
    """
    Find the file path in the 

    Parameters
    ----------
    statistics_path : str
        path of the statistics files where to find the assets path
    app : str
        app where there is the asset name
    asset_name : str
        asset name to search in the data json
    type : str
        images, audio, or video

    Returns
    -------
    str
        file path of the asset
    """

    cmd = f"grep '{asset_name}' {statistics_path}/{app}_{type}.json"
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output, error = process.communicate()
    try:
        return output.split()[1][1:-2].split(os.path.sep, 5)[-1]
    except IndexError:
        return None

def get_file_hash(file_path: str, hash_function, block_size=65536) -> str:
        with open(file_path, "rb", buffering=0) as f:
            for chunk in iter(lambda: f.read(block_size), b""):
                hash_function.update(chunk)
        return hash_function.hexdigest()

def sha256sum(file_path: str) -> str:
    return get_file_hash(file_path, sha256())

def find_modified_assets(app: str, type: str) -> tuple:
    """
    Find the modified assets in the directory

    Parameters
    ----------
    app : str
        app name
    type : str
        OceanLotus, LSB or audio

    Returns
    -------
    tuple
        if type is OceanLotus or LSB a tuple containing squares and sequential assets
        if type is audio a list containing the assets modified
    """
    assets = list()
    seq = list()
    sq = list()
    
    if type == 'audio':
        paths = glob.glob(os.path.join('..', '..', 'assets', 'stego_assets', type, app, '*'))
    else:
        paths = glob.glob(os.path.join('..', '..', 'assets', 'stego_assets', type, '*', app, '*'))
        
    for p in paths:
        if type == 'audio':
            assets += [os.path.join(p, a) for a in os.listdir(p)]
            return assets
        elif type == 'LSB' or type == 'OceanLotus':
            if 'Sequential' in p:
                seq += [os.path.join(p, i) for i in os.listdir(p)]
            elif 'Squares' in p:
                sq += [os.path.join(p, i) for i in os.listdir(p)]
            
    return seq, sq

def eliminate_dupilcates(combinations: list) -> list:
    """
    Eliminate duplicated for a list of combinations

    Parameters
    ----------
    combinations : list
        list of combinations

    Returns
    -------
    list
        list containing the combinations with the removed duplicates 
    """
    comb_new = list()
    for comb in combinations:

        if len(comb) > 1:
            unique = {}
            for path in comb:
                filename = os.path.basename(path)
                if filename not in unique:
                    unique[filename] = path
            comb_new.append(tuple(unique.values()))
        else:
            comb_new.append(comb)

    return comb_new

def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters, k=length))

def generate_random_dname():
    """
    Generate random dname for the certificate

    Returns
    -------
    str
        random dname
    """
    cn = random.choice(config.common_names) + "." + random_string(5)  # Random subdomain
    ou = random.choice(config.org_units)
    o = random.choice(config.organizations)
    l = random.choice(config.cities)
    s = random.choice(config.states)
    c = random.choice(config.countries)

    dname = f"CN={cn}, OU={ou}, O={o}, L={l}, S={s}, C={c}"
    return dname
    
def generate_keypair(keystore_path: str, alias: str, keystore_password: str, key_password: str):
    """
    Generate keypairs inside the keystore, with an alias, a keystore password and a password for accessing the key. Used
    for signing the new apk

    Parameters
    ----------
    keystore_path : str
        path of the keystore where to save the keys
    alias : str
        alias of the key
    keystore_password : str
        keystore password for accessing the keystore
    key_password : str
        key password for accessing the key given the alias
    """
    dname = generate_random_dname()
    command = [
        'keytool', '-genkeypair', '-v', 
        '-keystore', keystore_path,
        '-keyalg', 'RSA', 
        '-keysize', '2048', 
        '-validity', '10000', 
        '-alias', alias,
        '-dname', dname,
        '-storepass', keystore_password,
        '-keypass', key_password
    ]
    
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT).strip()
        return output.decode(errors="replace")
    except subprocess.CalledProcessError as e:
        logger.info(f'Error during key creation {e.output.decode(errors="replace")}')

def read_data(data_rebuilt: str) -> tuple:
    """
    Read the data about rebuilt combinations

    Parameters
    ----------
    data_rebuilt : str
        path of the file to read

    Returns
    -------
    tuple
        data read, and the combinations done
    """
    with open(data_rebuilt, 'r') as f_json:
        data = json.load(f_json)
    
    done = list()
    for k in data.keys():
        done.append(tuple(data[k][0]))
    
    return data, done