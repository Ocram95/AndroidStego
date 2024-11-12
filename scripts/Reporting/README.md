## Reassemble APK

The directory contains the scripts to get the reports from Virus Total.

Execute the script `report.py` with

```
python report.py [-h] [--input_path INPUT_PATH] [--output_path OUTPUT_PATH] --vt_key VT_KEY

Report with VT

optional arguments:
  -h, --help            show this help message and exit
  --input_path INPUT_PATH
                        Path to the input apks. Default: /mnt/Stegomalware/APK_Stego/apk/apk_stego
  --output_path OUTPUT_PATH
                        Path where to save the report. Default: /mnt/Stegomalware/APK_Stego/apk/reports/vt
  --vt_key VT_KEY       API key VirusTotal
```