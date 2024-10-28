from PIL import Image
import os
import numpy as np
import subprocess

def get_images(path):
	images = []
	for dirpath, dirnames, filenames in os.walk(path):
		for filename in filenames:
			if filename.endswith(".png"):
				file_path = os.path.join(dirpath, filename)
				images.append(file_path)
	return images

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

def parse_grey_image(image_path):
	with Image.open(image_path) as im:
		l, a = im.split()
		lll   = np.array(l).reshape(-1)
		alpha = np.array(a).reshape(-1)
		width, height = im.size
		l_in_bits = []
		alpha_in_bits = []
		for x in range(len(lll)):
			l_in_bits.append('{0:08b}'.format(lll[x]))
			alpha_in_bits.append('{0:08b}'.format(alpha[x]))
		
		return l_in_bits, alpha_in_bits, width, height

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

def decode_ocean_RGB(r, g, b, channels, pixel_index):
	extracted_secret_in_bits = []
	for x in range(len(r)):
		if x >= pixel_index - 1:
			if "R" in channels:
				extracted_secret_in_bits.append(r[x][-3:])
			if "G" in channels:
				extracted_secret_in_bits.append(g[x][-3:])
			if "B" in channels:
				extracted_secret_in_bits.append(b[x][-2:])
	flattened_list = [char for item in extracted_secret_in_bits for char in item]
	return flattened_list

def decode_classic_LA(l):
	extracted_secret_in_bits = []
	for x in range(len(l)):
		extracted_secret_in_bits.append(l[x][-1:])
	return extracted_secret_in_bits

def decode_LSB_palette_classic(image):
	extracted_secret_in_bits = []
	palette = image.getpalette()
	r = g = b = []
	for i in range(0, len(palette), 3):
		extracted_secret_in_bits.append('{0:08b}'.format(palette[i])[-1])
		extracted_secret_in_bits.append('{0:08b}'.format(palette[i+1])[-1])
		extracted_secret_in_bits.append('{0:08b}'.format(palette[i+2])[-1])
	return extracted_secret_in_bits

def decode_LSB_mode1(image):
	extracted_secret_in_bits = []
	width, height = image.size
	pixels = image.load
	new_pixels = []
	for y in range(height):
		for x in range(width):
			pixel_value = image.getpixel((x,y))
			if pixel_value == 0:
				extracted_secret_in_bits.append('0')
			elif pixel_value == 255:
				extracted_secret_in_bits.append('1')
	return extracted_secret_in_bits

def decode_ocean_palette_classic(image):
	extracted_secret_in_bits = []
	palette = image.getpalette()
	r = g = b = []
	for i in range(0, len(palette), 3):
		extracted_secret_in_bits.append('{0:08b}'.format(palette[i])[5:])
		extracted_secret_in_bits.append('{0:08b}'.format(palette[i+1])[5:])
		extracted_secret_in_bits.append('{0:08b}'.format(palette[i+2])[6:])
	flattened_list = [char for item in extracted_secret_in_bits for char in item]
	return flattened_list

def split_in_9(image):
	width, height = image.size
	parts = []

	# Calculate the approximate width and height of each block
	block_width = width // 3
	block_height = height // 3

	for row in range(3):
		for col in range(3):
			# Calculate the coordinates for each block
			x1 = col * block_width
			y1 = row * block_height

			# For the last column/row, adjust the size to include any remainder
			x2 = (x1 + block_width) if col < 2 else width
			y2 = (y1 + block_height) if row < 2 else height

			# Crop the image and append the part to the list
			part = image.crop((x1, y1, x2, y2))
			parts.append(part)

	# Save the 9 parts
	for i, part in enumerate(parts):
		output_path = f'part_{i + 1}.png'
		part.save(output_path)

	tmp = []
	for filename in os.listdir("."):
		if filename.lower().endswith(".png"):
			if "1" in filename or "5" in filename or "9" in filename:
				tmp.append(filename)
	list_image_parts = sorted(tmp, key=lambda x: int(x.split('_')[-1].split('.')[0]))

	return list_image_parts

def split_secret(secret):
	list_split = []
	total_length = len(secret)

	length_part = total_length // 3
	remains = total_length % 3

	list_split.append(secret[:length_part + remains])
	list_split.append(secret[length_part + remains:2 * length_part + remains])
	list_split.append(secret[2 * length_part + remains:])

	return list_split

def secret_correctly_encoded(secret_in_chunks, output):
	length = min(len(secret_in_chunks), len(output))
	for x in range(length):
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

def divide_string(string, lengths):
	split_list = []

	start = 0
	while start < len(string):
		for length in lengths:
			substring = string[start:start + length]
			split_list.append(substring)
			start += length

	return split_list

# secret = '''Class.forName("dalvik.system.DexClassLoader");Object objecte = this.b.getClassLoader();Method methode=new DexClassLoader(filee.getPath(),filee.getParent(),null,((ClassLoader)objecte)).loadClass("sdk.fkgh.mvp.SdkEntry");methode.setAccessible(true);methode.invoke(null,this.b,this.c,this.a);}ag.g[8]="rrqnDG4dja7Ga5ZdAuD77CY";ag.g[9]="xodOhs";'''
secret = '''methode.setAccessible(true);methode.invoke(null,this.b,this.c,this.a);ag.g[8]="rrqnDG4dja7Ga5ZdAuD77CY";ag.g[9]="xodOhs"'''

secret_in_bits = read_secret(secret)
secret_in_chunks = [secret_in_bits[i:i+1] for i in range(0, len(secret_in_bits), 1)]

images = get_images('../LSB/sequential/')
for image in images[:]:
	print(image)
	img = Image.open(image)
	mode = img.mode
	if mode == "RGB" or mode == "RGBA":
		r,g,b,_a,_w,_h = parse_RGB_image(image)
		output = decode_classic_RGB(r,g,b, 1, "RGB", 1)
		secret_correctly_encoded(secret_in_chunks, output)
	elif mode == "LA":
		l, _a, _w, _h = parse_grey_image(image)
		output = decode_classic_LA(l)
		secret_correctly_encoded(secret_in_chunks, output)
	elif mode == "P":
		output = decode_LSB_palette_classic(img)
		secret_correctly_encoded(secret_in_chunks, output)
	elif mode == '1':
		output = decode_LSB_mode1(img)
		secret_correctly_encoded(secret_in_chunks, output)


images = get_images('../LSB/Squares/')
secret_split = split_secret(secret)

for image in images[1:]:
	print(image)
	img = Image.open(image)
	mode = img.mode
	if mode == "RGB" or mode == "RGBA":
		list_image_parts = split_in_9(img)
		for x in range(len(list_image_parts)):
			image_tmp = list_image_parts[x]
			secret_tmp = secret_split[x]
			secret_tmp_in_bits = read_secret(secret_tmp)
			secret_tmp_in_chunks = [secret_tmp_in_bits[i:i+1] for i in range(0, len(secret_tmp_in_bits), 1)]
			r,g,b,_a,_w,_h = parse_RGB_image(image_tmp)
			output = decode_classic_RGB(r,g,b, 1, "RGB", 1)
			secret_correctly_encoded(secret_tmp_in_chunks, output)
	# elif mode == "LA":
	# 	print(image)
	# 	list_image_parts = split_in_9(img)
	# 	for x in range(len(list_image_parts)):
	# 		image_tmp = list_image_parts[x]
	# 		secret_tmp = secret_split[x]
	# 		l, _a, _w, _h = parse_grey_image(image_tmp)
	# 		secret_tmp_in_bits = read_secret(secret_tmp)
	# 		secret_tmp_in_chunks = [secret_tmp_in_bits[i:i+1] for i in range(0, len(secret_tmp_in_bits), 1)]
	# 		print(secret_tmp_in_chunks)
	# 		output = decode_classic_LA(l)
	# 		print(output)
	# 		secret_correctly_encoded(secret_tmp_in_chunks, output)
	# 	break
	elif mode == '1':
		list_image_parts = split_in_9(img)
		for x in range(len(list_image_parts)):
			image_tmp = list_image_parts[x]
			secret_tmp = secret_split[x]
			secret_tmp_in_bits = read_secret(secret_tmp)
			secret_tmp_in_chunks = [secret_tmp_in_bits[i:i+1] for i in range(0, len(secret_tmp_in_bits), 1)]
			output = decode_LSB_mode1(Image.open(image_tmp))
			secret_correctly_encoded(secret_tmp_in_chunks, output)


images = get_images('../OceanLotus/Sequential/')

for image in images[:]:
	print(image)
	img = Image.open(image)
	mode = img.mode
	if mode == "RGB" or mode == "RGBA":
		r,g,b,_a,_w,_h = parse_RGB_image(image)
		output = decode_ocean_RGB(r,g,b, "RGB", 1)
		secret_correctly_encoded(secret_in_chunks, output)
	elif mode == "P":
		output = decode_ocean_palette_classic(img)
		secret_correctly_encoded(secret_in_chunks, output)

images = get_images('../OceanLotus/Squares/')
secret_split = split_secret(secret)

for image in images[:]:
	print(image)
	img = Image.open(image)
	mode = img.mode
	if mode == "RGB" or mode == "RGBA":
		list_image_parts = split_in_9(img)
		for x in range(len(list_image_parts)):
			image_tmp = list_image_parts[x]
			secret_tmp = secret_split[x]
			secret_tmp_in_bits = read_secret(secret_tmp)
			secret_tmp_in_chunks = [secret_tmp_in_bits[i:i+1] for i in range(0, len(secret_tmp_in_bits), 1)]
			r,g,b,_a,_w,_h = parse_RGB_image(image_tmp)
			output = decode_ocean_RGB(r,g,b, "RGB", 1)
			secret_correctly_encoded(secret_tmp_in_chunks, output)


command = "rm part_*"
process = subprocess.Popen(command, shell=True)
process.wait()





















