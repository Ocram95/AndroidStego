# Statistics extractor

This directory contains the scripts to create an resources dataset from a known set of applications.

1. info_extractor.py [-h] [--decode] [--statistics] [--input_apks INPUT_APKS] to extract info from a known set of application. 
        
        optional arguments:

        -h, --help            show this help message and exit
    
        --decode              Whether or not to decode apks
    
        --statistics          Whether or not to extract statistics
     
        --input_apks INPUT_APKS 
                              Path to input apks. Default: /mnt/Stegomalware/APK_Stego/
    
2. resource_extractor.py to select resources with specific features