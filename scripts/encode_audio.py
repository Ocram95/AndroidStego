import os
import subprocess

audio_mp3 = []
audio_wav = []

main_folder = '../assets'
for dirpath, dirnames, filenames in os.walk(main_folder):
	for filename in filenames:
		if filename.endswith(".mp3"):
			file_path = os.path.join(dirpath, filename)
			audio_mp3.append(file_path)
		elif filename.endswith(".wav"):
			file_path = os.path.join(dirpath, filename)
			audio_wav.append(file_path)

secret = """'59.183.111.96:57926/i*d*58.47.106.191:51900/bin.sh*d*117.213.92.42:56783/Mozi.m'"""

for audio in audio_mp3[:]:
	print(audio)
	command = "./hideme " + audio + " \"" + secret + "\""
	process = subprocess.Popen(command, shell=True)
	process.wait()
	command = "mv output.mp3 " + audio.replace("assets", "assets_stego_empty")
	process = subprocess.Popen(command, shell=True)
	process.wait()

for audio in audio_wav[:]:
	print(audio)
	command = "./hideme " + audio + " \"" + secret + "\""
	process = subprocess.Popen(command, shell=True)
	process.wait()
	command = "mv output.wav " + audio.replace("assets", "assets_stego_empty")
	process = subprocess.Popen(command, shell=True)
	process.wait()