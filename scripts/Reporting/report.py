from VirusTotal import VirusTotal
from argparse import ArgumentParser
import os

def get_arguments()-> ArgumentParser:
    
    parser = ArgumentParser(description="Reassemble the apk with the stegoassets. Requirements: apktool, apksigner, zipalign and budledecompile")
    parser.add_argument('--input_path', type=str, help="Path to the input apks. Default: /mnt/Stegomalware/APK_Stego/apk/apk_stego")
    parser.add_argument('--output_path', type=str, help="Path where to save the report. Default: /mnt/Stegomalware/APK_Stego/apk/reports/vt")
    parser.add_argument('--vt_key', type=str, required=True, help="API key VirusTotal")
    args = parser.parse_args()
    
    return args

def main():
    
    args = get_arguments()
    input_path = args.input_path
    if input_path is None:
        input_path = os.path.join("/mnt", 'Stegomalware', 'APK_Stego', 'apk', 'apk_stego')
    output_path = args.output_path
    if output_path is None:
        output_path = os.path.join("/mnt", 'Stegomalware', 'APK_Stego', 'apk', 'reports', 'vt')
    vt_key = args.vt_key
    
    vt = VirusTotal(vt_key, output_path)
    
    done_reports = [app.replace('.json', '.apk') for app in os.listdir(output_path)]
    
    for app in os.listdir(input_path):
        if app in done_reports:
            continue
        print(app)
        vt.analyse_apk(os.path.join(input_path, app))   

if __name__ == "__main__":
    main()