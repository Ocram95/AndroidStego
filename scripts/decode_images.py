from PIL import Image
import os
import numpy as np


def parse_RGB_image(image_path):
	with Image.open(image_path) as im:
		#it returns RGB or RGBA (if alpha channel is present)
		mode = im.mode
		#alpha channel
		a = []
		if len(mode) == 3:
			r,g,b = im.split()
			alpha = []
		else:
			r,g,b,a = im.split()
			alpha = np.array(a).reshape(-1)
		red   = np.array(r).reshape(-1)
		green = np.array(g).reshape(-1)
		blue  = np.array(b).reshape(-1)
	
	width, height = im.size

	red_in_bits   = []
	green_in_bits = []
	blue_in_bits  = []
	alpha_in_bits = []

	for x in range(len(red)):
		red_in_bits.append('{0:08b}'.format(red[x]))
		green_in_bits.append('{0:08b}'.format(green[x]))
		blue_in_bits.append('{0:08b}'.format(blue[x]))
		if len(alpha) != 0:
			alpha_in_bits.append('{0:08b}'.format(alpha[x]))

	return red_in_bits, green_in_bits, blue_in_bits, alpha_in_bits, width, height

def decode_classic_RGB(r, g, b, bits, channels, pixel_index):
	extracted_secret_in_bits = []
	for x in range(len(r)):
		if x >= pixel_index - 1:
			if "R" in channels:
				extracted_secret_in_bits.append(r[x][-bits:])
			if "G" in channels:
				extracted_secret_in_bits.append(g[x][-bits:])
			if "B" in channels:
				extracted_secret_in_bits.append(b[x][-bits:])
	return extracted_secret_in_bits

def secret_correctly_encoded(secret_in_chunks, output):
	for x in range(len(secret_in_chunks)):
		#check if the x-th element of the secret injected is equal to the one extracted
		if(secret_in_chunks[x] != output[x]):
			#sometimes it is possible that the secret injected can be something like 
			#['000', '010', '10'], i.e., the last element is different in terms of size w.r.t.
			#the other elements. Thus, the following check deals with this situations.
			if secret_in_chunks[x] != output[x][-len(secret_in_chunks[x]):]:
				print("ERROR")
				return
	print("Secret correctly decoded!")

def read_secret(secret_path):
	secret_in_bits = ''.join(format(ord(bit), '08b') for bit in secret_path)
	return secret_in_bits


images = []
main_folder = 'assets_stego'
for dirpath, dirnames, filenames in os.walk(main_folder):
	for filename in filenames:
		if filename.endswith(".png") and ("_seq" in filename or "_squares" in filename):
			file_path = os.path.join(dirpath, filename)
			images.append(file_path)

secret = '''Class.forName("dalvik.system.DexClassLoader");Object objecte = this.b.getClassLoader();Method methode=new DexClassLoader(filee.getPath(),filee.getParent(),null,((ClassLoader)objecte)).loadClass("sdk.fkgh.mvp.SdkEntry");methode.setAccessible(true);methode.invoke(null,this.b,this.c,this.a);}ag.g[8]="rrqnDG4dja7Ga5ZdAuD77CY";ag.g[9]="xodOhs";'''



for image in images[:]:
	img = Image.open(image)
	mode = img.mode
	if mode == "RGB" or mode == "RGBA":
		if "_classic" in image:
			if "_seq" in image:
				secret_in_bits = read_secret(secret)
				secret_in_chunks = [secret_in_bits[i:i+1] for i in range(0, len(secret_in_bits), 1)]
				r,g,b,a,width,height = parse_RGB_image(image)
				output = decode_classic_RGB(r,g,b, 1, "RGB", 1)
				secret_correctly_encoded(secret_in_chunks, output)
			elif "_squares" in image:
				print("TODO")
		elif "_ocean" in image:
			if "_seq" in image:
				print("TODO")
			elif "_squares" in image:
				print("TODO")
