from tool import Apktool, ApkSigner, Zipalign
from toolbundledecompiler import BundleDecompiler
from loguru import logger
import subprocess
import os
import glob

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
    print(cmd)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output, error = process.communicate()
    
    return output.split()[1][1:-2].split(os.path.sep, 5)

def find_modified_assets(app:str, type: str) -> tuple:
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
    for p in glob.glob(os.path.join('..', 'assets', 'stego_assets', type, app, '*')):
        if type == 'audio':
            assets += [a for a in os.listdir(p)]
            return assets
        elif type == 'LSB' or type == 'OceanLotus':
            if 'Sequential' in p:
                seq += [i for i in os.listdir(p)]
            elif 'Squares' in p:
                sq += [i for i in os.listdir(p)]
            return seq, sq
    
    