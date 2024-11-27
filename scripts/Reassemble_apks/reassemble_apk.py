from loguru import logger
from argparse import ArgumentParser
import os
import json
import subprocess
import glob
from utils import find_file_path, find_modified_resources, check_external_tool_dependencies, combine, sha256sum, eliminate_dupilcates, generate_keypair
from utils import read_data
from shutil import copy2, copytree, rmtree
from tool import Apktool, ApkSigner, Zipalign
from loguru import logger
from typing import Optional

def get_arguments() -> ArgumentParser:
    
    parser = ArgumentParser(description="Reassemble the apk with the stegoassets. Requirements: apktool, apksigner, zipalign and budledecompile")
    parser.add_argument('--decoded_path', type=str, help="Path to the decoded apks. Default: /mnt/Stegomalware/APK_Stego/decoded")
    parser.add_argument('--output_path', type=str, help="Path where to save the new apk. Default: /mnt/Stegomalware/APK_Stego/apk/apk_stego")
    args = parser.parse_args()
    
    return args

def rebuild(source_dir_path: str, output_apk_path: str, keystore_path: str, keystore_password: str, 
            alias: str, key_password: str) -> str:
    """
    Rebuild the applications

    Parameters
    ----------
    source_dir_path : str
        directory containing files of the app to rebuild
    output_apk_path : str
        path of the output apk
    keystore_path : str
        path of the keystore where to save the keys
    keystore_password : str
        keystore password for accessing the keystore
    alias : str
        alias of the key
    key_password : str
        key password for accessing the key given the alias

    Returns
    -------
    str
        hash of the new application
    """
    apktool = Apktool()
    apksigner = ApkSigner()
    zipalign = Zipalign()
    
    output_apk_path = os.path.join(output_apk_path, 'output.apk')
    
    # build the application
    apktool.build(source_dir_path, output_apk_path)
    # if the build goes well the output_apk_path contains the new apk
    try:
        logger.info(f"App Rebuilt ...")
    
        # sign the application and realign it
        apksigner.resign(output_apk_path,
                        keystore_path,
                        keystore_password,
                        alias,
                        key_password)
        """command = [
                    "./sign_apk.sh",  # Path to your shell script
                    new_path,
                    keystore_path,
                    alias,
                    keystore_password,
                    key_password
                ]
        """
        # command = " ".join(command)
        # result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        # print(result.stdout, result.stderr)
        # subprocess.check_call(command, shell=False)
        # os.system(command)
        zipalign.align(output_apk_path)
        # compute the hash of the rebuilt application
        hash = sha256sum(output_apk_path)
        # rename the app with the hash
        new_path = os.path.join(output_apk_path.rsplit(os.path.sep, 1)[0], f'{hash}.apk')
        os.rename(output_apk_path, new_path)
        logger.info(f"Signed and aligned ...")
    except FileNotFoundError as e:
        print(e)
        return None
    
    return hash

def copy_and_reassemble(combination: tuple, statistics_path: str, app: str, output_path: str, decoded_path: str,
                        keystore_path: str, keystore_password: str, alias: str, key_password: str) -> Optional[tuple]:
    """
    Copy and reassemble the application

    Parameters
    ----------
    combination : tuple
        combination of resources to copy inside the directory
    statistics_path : str
        path of the statistics where to find the path where to copy the new resources
    app : str
        name of the application to modify
    output_path : str
        output path where to store the new application
    decoded_path : str
        path of the apps decoded
    keystore_path : str
        path of the keystore where to save the keys
    keystore_password : str
        keystore password for accessing the keystore
    alias : str
        alias of the key
    key_password : str
        key password for accessing the key given the alias
        
    Returns
    -------
    Optional[tule]
        hash of the new app, combination and path of the resources
    """
    dst_path = os.path.join(decoded_path, 'decoded_copy')
    src_path = os.path.join(decoded_path, 'decoded_original')
    resources = list()
    if os.path.exists(os.path.join(dst_path, app)):
        rmtree(os.path.join(dst_path, app))
    copytree(os.path.join(src_path, app), os.path.join(dst_path, app))
    logger.info(f"Copied dir decoded ...")
    logger.info(f"Working with the combination {combination} ...")
    for c in combination:
        typology, resource_name = c.rsplit(os.path.sep, 2)[-2:]
        # find the file path to change
        resource_path = find_file_path(statistics_path, app, resource_name, typology)
        if resource_path is not None:
            resources.append(resource_path)
            copy2(c, os.path.join(dst_path, resource_path))
        
            logger.info(f"Copied resources {c} in {resource_path} ...")

    hash = rebuild(os.path.join(dst_path, app), output_path, keystore_path, keystore_password, 
                   alias, key_password)
    rmtree(os.path.join(dst_path, app))
    if hash is not None:
        return hash, [combination, tuple(resources)]
    else:
        return None

def main():
    args = get_arguments()
    decoded_path = args.decoded_path
    if decoded_path is None:
        decoded_path = os.path.join('/mnt', 'Stegomalware', 'APK_Stego', 'decoded') 
    
    output_path = args.output_path
    if output_path is None:
        output_path = os.path.join('/mnt', 'Stegomalware', 'APK_Stego', 'apk', 'apk_stego')
    
    statistics_path = os.path.join('..', 'statistics_extractor', 'data')

    done_apks = [done.replace('.json', '') for done in os.listdir('./data_rebuilt')]
    # loop over all the apps to rebuild
    for app in os.listdir(os.path.join(decoded_path, 'decoded_original')):
        # if app in done_apks:
        #    continue
        if app not in ['amazon-shopping', 'Telegram', 'bulletecho', 'candyCrush', 'Eurospin', 'flixbus', 'duolingo']:
            continue
        logger.info(f"Starting with {app} ...")
        # find the resources modified in the resources directory
        try:
            oc_seq, oc_sq = find_modified_resources(app, 'OceanLotus')
        except TypeError as e:
            print(e)
        try:
            lsb_seq, lsb_sq = find_modified_resources(app, 'LSB')
        except TypeError as e:
            print(e)
        try:
            audio = find_modified_resources(app, 'audio')
        except TypeError as e:
            print(e)
        
        # find all combinations
        elements = list()
        for e in [oc_seq, oc_sq, lsb_seq, lsb_sq, audio]:
            if e is not None and len(e) != 0 and type(e) != tuple:
                elements += e
        combinations = combine(elements)
        # eliminate duplications in the combinations
        combinations = set(eliminate_dupilcates(combinations))

        # set the keys for the signing keys
        keystore_password = "obfuscation_password"
        keystore_path = os.path.join(os.path.dirname(__file__), "keys", f"{app}.jks")
        key_password = "obfuscation_password"
        
        data_rebuilt = os.path.join(os.path.dirname(__file__), "data_rebuilt", f"{app}.json")
        try:
            data, done_comb = read_data(data_rebuilt)
        except FileNotFoundError:
            data = dict()
            done_comb = list()

        for i, combination in enumerate(combinations):
            if combination in done_comb:
                continue
            alias = f'{app}_{i}'
            # generate the keypairs for signing the app
            generate_keypair(keystore_path, alias, keystore_password, key_password)
            # copy files and reassemble the apk
            result = copy_and_reassemble(combination, statistics_path, app, output_path, decoded_path,
                                         keystore_path, keystore_password, alias, key_password)
            if result is not None:
                data[result[0]] = result[1] 
        with open(data_rebuilt, 'w') as f_json:
            f_json.write(json.dumps(data, indent=2))


if __name__ == '__main__':
    logger.remove()
    logger.add('logger_repackaging1.log', format="{time:DD/MM HH:mm} - {message}")
    main()
    # pass