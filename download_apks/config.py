import os
import json

with open('apps_name.txt', 'r') as file:
    apps = file.read().split('\n')

json_file = {
    "options": {
      "arch": "arm64-v8a",
      "outDir": "/mnt/FileSources/APK_Stego",
      "type": "apk"
    },
    "apps": [{"repo": f"{app}", "outFile": f"{app}"} for app in apps[:-1]]
}

with open("apps.json", "w") as fp:
    json.dump(json_file, fp)
