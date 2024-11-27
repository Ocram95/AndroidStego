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

	return red_in_bits, green_in_bits, blue_in_bits, alpha_in_bits

def parse_LA_image(image_path):
	with Image.open(image_path) as im:
		l, a = im.split()
		lll   = np.array(l).reshape(-1)
		alpha = np.array(a).reshape(-1)
		l_in_bits = []
		alpha_in_bits = []
		for x in range(len(lll)):
			l_in_bits.append('{0:08b}'.format(lll[x]))
			alpha_in_bits.append('{0:08b}'.format(alpha[x]))
		
		return l_in_bits, alpha_in_bits

def decode_LSB_RGB(r, g, b):
	extracted_secret_in_bits = []
	for x in range(len(r)):
		extracted_secret_in_bits.append(r[x][-1])
		extracted_secret_in_bits.append(g[x][-1])
		extracted_secret_in_bits.append(b[x][-1])
	return extracted_secret_in_bits

def decode_OCEAN_RGB(r, g, b):
	extracted_secret_in_bits = []
	for x in range(len(r)):
		extracted_secret_in_bits.append(r[x][-3:])
		extracted_secret_in_bits.append(g[x][-3:])
		extracted_secret_in_bits.append(b[x][-2:])
	flattened_list = [char for item in extracted_secret_in_bits for char in item]
	return flattened_list

def decode_LSB_LA(l):
	extracted_secret_in_bits = []
	for x in range(len(l)):
		if l[x][-1] == '1':
			extracted_secret_in_bits.append('1')
		else:
			extracted_secret_in_bits.append('0')
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

def decode_LSB_palette(image):
	extracted_secret_in_bits = []
	palette = image.getpalette()
	r = g = b = []
	for i in range(0, len(palette), 3):
		extracted_secret_in_bits.append('{0:08b}'.format(palette[i])[-1])
		extracted_secret_in_bits.append('{0:08b}'.format(palette[i+1])[-1])
		extracted_secret_in_bits.append('{0:08b}'.format(palette[i+2])[-1])
	return extracted_secret_in_bits, len(palette)

def decode_OCEAN_palette(image):
	extracted_secret_in_bits = []
	palette = image.getpalette()
	r = g = b = []
	for i in range(0, len(palette), 3):
		extracted_secret_in_bits.append('{0:08b}'.format(palette[i])[-3:])
		extracted_secret_in_bits.append('{0:08b}'.format(palette[i+1])[-3:])
		extracted_secret_in_bits.append('{0:08b}'.format(palette[i+2])[-2:])
	flattened_list = [char for item in extracted_secret_in_bits for char in item]
	return flattened_list, len(palette)

def split_in_9(image):
	im = Image.open(image)
	width, height = im.size
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

			# Crop the im and append the part to the list
			part = im.crop((x1, y1, x2, y2))
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
	if secret_in_chunks == output[:len(secret_in_chunks)]:
		print("Secret correctly decoded!")
	else:
		print("Error")

def secret_correctly_encoded_palette(secret_in_chunks, output, len_palette):
	if secret_in_chunks[:len_palette] == output[:len_palette]:
		print("Secret correctly decoded!")
	else:
		print("Error")

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


def bits_to_string(bits):
	result = ""
	for i in range(0, len(bits), 8):
		byte = bits[i:i+8]
		byte_str = ''.join(map(str, byte))
		byte_int = int(byte_str, 2)
		result += chr(byte_int)

	return result


secret = '''methode.setAccessible(true);methode.invoke(null,this.b,this.c,this.a);ag.g[8]="rrqnDG4dja7Ga5ZdAuD77CY";ag.g[9]="xodOhs"'''


secret_in_bits = read_secret(secret)
secret_in_chunks = [secret_in_bits[i:i+1] for i in range(0, len(secret_in_bits), 1)]


images = get_images('../resources/stego_resources/LSB/Sequential/')
for image in images:
	img = Image.open(image)
	mode = img.mode
	if mode == "RGB" or mode == "RGBA":
		r,g,b,_a = parse_RGB_image(image)
		output = decode_LSB_RGB(r,g,b)
		secret_correctly_encoded(secret_in_chunks, output)
		print(bits_to_string(output)[:len(secret)])
	elif mode == "LA":
		l, _a = parse_LA_image(image)
		output = decode_LSB_LA(l)
		secret_correctly_encoded(secret_in_chunks, output)
		print(bits_to_string(output)[:len(secret)])
	elif mode == "1":
		img = Image.open(image)
		output = decode_LSB_mode1(img)
		secret_correctly_encoded(secret_in_chunks, output)
	elif mode == "P":
		img = Image.open(image)
		output, len_palette = decode_LSB_palette(img)
		secret_correctly_encoded_palette(secret_in_chunks, output, len_palette)

images = get_images('../resources/stego_resources/OceanLotus/Sequential/')
for image in images:
	img = Image.open(image)
	mode = img.mode
	if mode == "RGB" or mode == "RGBA":
		r,g,b,_a = parse_RGB_image(image)
		output = decode_OCEAN_RGB(r,g,b)
		secret_correctly_encoded(secret_in_chunks, output)
	elif mode == "P":
		img = Image.open(image)
		output, len_palette = decode_OCEAN_palette(img)
		secret_correctly_encoded_palette(secret_in_chunks, output, len_palette)


secret_split = split_secret(secret)

images = get_images('../resources/stego_resources/LSB/Squares/')
for image in images:
	img = Image.open(image)
	mode = img.mode
	if mode == "RGB" or mode == "RGBA":
		list_image_parts = split_in_9(image)
		for x in range(len(list_image_parts)):
			image_tmp = list_image_parts[x]
			tmp_image = Image.open(image_tmp)
			tmp_width, tmp_height = tmp_image.size
			secret_tmp = secret_split[x]
			tmp_r,tmp_g,tmp_b,tmp_a = parse_RGB_image(image_tmp)
			secret_tmp_in_bits = read_secret(secret_tmp)
			secret_tmp_in_chunks = [secret_tmp_in_bits[i:i+1] for i in range(0, len(secret_tmp_in_bits), 1)]
			output = decode_LSB_RGB(tmp_r,tmp_g,tmp_b)
			secret_correctly_encoded(secret_tmp_in_chunks, output)



images = get_images('../resources/stego_resources/OceanLotus/Squares/')
for image in images:
	img = Image.open(image)
	mode = img.mode
	if mode == "RGB" or mode == "RGBA":
		list_image_parts = split_in_9(image)
		for x in range(len(list_image_parts)):
			image_tmp = list_image_parts[x]
			tmp_image = Image.open(image_tmp)
			tmp_width, tmp_height = tmp_image.size
			secret_tmp = secret_split[x]
			tmp_r,tmp_g,tmp_b,tmp_a = parse_RGB_image(image_tmp)
			secret_tmp_in_bits = read_secret(secret_tmp)
			secret_tmp_in_chunks = [secret_tmp_in_bits[i:i+1] for i in range(0, len(secret_tmp_in_bits), 1)]
			output = decode_OCEAN_RGB(tmp_r,tmp_g,tmp_b)
			secret_correctly_encoded(secret_tmp_in_chunks, output)














# list_image_parts = split_in_9("test_LSB_squares_LA.png")
# for x in range(len(list_image_parts)):
# 	image_tmp = list_image_parts[x]
# 	tmp_image = Image.open(image_tmp)
# 	tmp_width, tmp_height = tmp_image.size
# 	secret_tmp = secret_split[x]
# 	tmp_l, _tmp_a = parse_LA_image(image_tmp)
# 	secret_tmp_in_bits = read_secret(secret_tmp)
# 	secret_tmp_in_chunks = [secret_tmp_in_bits[i:i+1] for i in range(0, len(secret_tmp_in_bits), 1)]
# 	output = decode_LSB_LA(tmp_l)
# 	secret_correctly_encoded(secret_tmp_in_chunks, output)
# 	print(output[:len(secret_tmp_in_chunks)])
# 	print(secret_tmp_in_chunks[:10])






































