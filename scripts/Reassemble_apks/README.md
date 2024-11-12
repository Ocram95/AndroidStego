## Reassemble APK

The directory contains the scripts to reassemble the application with the modified assets.

Execute the script with 

```
python reassemble_apk.py [-h] [--decoded_path DECODED_PATH] [--output_path OUTPUT_PATH]

Reassemble the apk with the stegoassets. Requirements: apktool, apksigner, zipalign and budledecompile

optional arguments:
  -h, --help            show this help message and exit
  --decoded_path DECODED_PATH
                        Path to the decoded apks. Default: /mnt/Stegomalware/APK_Stego/decoded/decoded_original
  --output_path OUTPUT_PATH
                        Path where to save the new apk. Default: /mnt/Stegomalware/APK_Stego/apk/apk_stego
```

where the decoded_path arg points to a directory organized as follows:
    - decoded_original, where the original decoded apps are stored. You can decode it manually by using `apktool d path/to/apk.apk -o path/to/decoded/original/apk/appName`
    - decoded_copy/, where the copied decoded apps will be stored

and the output_path points to a directory organized as follows:
    - apk_orginal/, where the original apks are stored.
    - apk_stego/, where the modified apks will be stored.

The directory `data_rebuilt` contains the json with the hashes of new rebuilt applications, and the combinations of modified assets and the path where to copy the asset.