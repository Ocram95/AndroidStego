import os
import subprocess
import re 

audio_mp3 = []
audio_wav = []

main_folder = '../assets/stego_assets/audio/'
for dirpath, dirnames, filenames in os.walk(main_folder):
	for filename in filenames:
		if filename.endswith(".mp3"):
			file_path = os.path.join(dirpath, filename)
			audio_mp3.append(file_path)
		elif filename.endswith(".wav"):
			file_path = os.path.join(dirpath, filename)
			audio_wav.append(file_path)

secret = """'59.183.111.96:57926/i*d*58.47.106.191:51900/bin.sh*d*117.213.92.42:56783/Mozi.m'"""

print(audio_mp3)
print(audio_wav)
# for audio in audio_mp3[:]:
# 	print(audio)
# 	command = "./hideme " + audio + " -f"
# 	process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# 	process.wait()
# 	stdout, stderr = process.communicate()
# 	output = stdout.decode('latin-1')
# 	match = re.search(r"Message: ('[^']*')", output)
# 	if match:
# 		message_value = match.group(1)
# 		if message_value[:len(secret)] == secret:
# 			print("Secret correctly decoded!")
# 		else:
# 			print("Error")
# 	else:
# 		print("Message field not found.")

# for audio in audio_wav[:]:
# 	print(audio)
# 	command = "./hideme " + audio + " -f"
# 	process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# 	process.wait()
# 	stdout, stderr = process.communicate()
# 	output = stdout.decode('latin-1')
# 	match = re.search(r"Message: ('[^']*')", output)
# 	if match:
# 		message_value = match.group(1)
# 		if message_value[:len(secret)] == secret:
# 			print("Secret correctly decoded!")
# 		else:
# 			print("Error")
# 	else:
# 		print("Message field not found.")


