# AndroidStego

This repository consists of real digital Android assets containing malicious payloads and URLs hidden via steganographic techniques.

Specifically:
- assets: it contains both images and audio files coming from 20 Android applications;
- audio: it contains all the audio files (both in .mp3 and .wav formats) hiding malicious URLs. The URLs have been hidden via the [AudioStego](https://github.com/danielcardeenas/AudioStego/tree/master) tool;
- LSB: it contains all the images hiding the malicious payload. The payload has been hidden via ad-hoc scripts in two different patterns (sequential and squares) in the first least significant bit of the red, green, and blue color channels.
- OceanLotus: it contains all the images hiding the malicious payload. The payload has been hidden via ad-hoc scripts in two different patterns (sequential and squares) mimicking the OceanLotus LSB steganographic method (i.e., 3 bits of the red and the green channels, 2 bits in blue color channel);
- Invoke-PSImage: it contains all the images hiding the malicious payload. The payload has been hidden via the [Invoke-PSImage](https://github.com/peewpw/Invoke-PSImage);
- scripts: it contains all the scripts used to generate and test this dataset:
    1. decode_images.py, encode_images.py and encode_audio.py to generate the dataset of stego resources;
    2. statistics_extractor/, directory that contains the code used to extract statistics from assets of applications (info_extractor.py) and select only certain assets (assets_extractor.py)
- data.xlsx: it contains a summary of the dataset.

The payload hidden in the images is part of the [Necro Trojan](https://securelist.com/necro-trojan-is-back-on-google-play/113881/) and malicious URLs hidden in the audio files are collected from [URLhase](https://urlhaus.abuse.ch/) repository. 