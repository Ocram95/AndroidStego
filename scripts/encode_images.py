import os
import subprocess
from PIL import Image
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

def encode_LSB_RGBA(r, g, b, alpha, secret_in_chunks, channels, pixel_index, width, height):
	index = 0
	for x in range(len(r)):
		if x >= pixel_index - 1:
			if index >= len(secret_in_chunks):
				break
			if index < len(secret_in_chunks):
				if "R" in channels:
					r[x] = r[x][:-len(secret_in_chunks[index])] + secret_in_chunks[index]
					index += 1
			if index < len(secret_in_chunks):
				if "G" in channels:
					g[x] = g[x][:-len(secret_in_chunks[index])] + secret_in_chunks[index]
					index += 1
			if index < len(secret_in_chunks):
				if "B" in channels:
					b[x] = b[x][:-len(secret_in_chunks[index])] + secret_in_chunks[index]
					index += 1

	new_pixels_list = []
	tmp_list = []
	for x in range(len(r)):
		tmp_red_int = int(r[x], 2)
		tmp_green_int = int(g[x], 2)
		tmp_blue_int = int(b[x], 2)
		if len(alpha) != 0:
			tmp_alpha_int = int(alpha[x], 2)
			tmp_list.append((tmp_red_int, tmp_green_int, tmp_blue_int, tmp_alpha_int))
		else:
			tmp_list.append((tmp_red_int, tmp_green_int, tmp_blue_int))
		if len(tmp_list) == width:
			new_pixels_list.append(tmp_list)
			tmp_list = []
	return new_pixels_list

def encode_LSB_LA(l, alpha, secret_in_chunks, pixel_index, width, height):
	index = 0
	for x in range(len(l)):
		if x >= pixel_index - 1:
			if index >= len(secret_in_chunks):
				break
			if index < len(secret_in_chunks):
				l[x] = l[x][:-len(secret_in_chunks[index])] + secret_in_chunks[index]
				index += 1
	new_pixels_list = []
	tmp_list = []
	for x in range(len(l)):
		tmp_l_int = int(l[x], 2)
		tmp_alpha_int = int(alpha[x], 2)
		tmp_list.append((tmp_l_int, tmp_alpha_int))
		if len(tmp_list) == width:
			new_pixels_list.append(tmp_list)
			tmp_list = []
	return new_pixels_list

def encode_LSB_palette_classic(image, secret_in_bits):
	while len(secret_in_bits) % 3 != 0:
		secret_in_bits += '0'
	palette = image.getpalette()
	secret_index = 0
	for i in range(0, len(palette), 3):
		if secret_index >= len(secret_in_bits):
			break

		r = palette[i]
		g = palette[i + 1]
		b = palette[i + 2]

		#---------| the least significant bit
		r = (r & ~1) | int(secret_in_bits[secret_index])
		g = (g & ~1) | int(secret_in_bits[secret_index + 1])
		b = (b & ~1) | int(secret_in_bits[secret_index + 2])

		palette[i] = r
		palette[i + 1] = g
		palette[i + 2] = b

		# Move to the next 3 secret bits
		secret_index += 3

	return palette

def encode_LSB_palette_ocean(image, secret_in_bits):
	while len(secret_in_bits) % 8 != 0:
		secret_in_bits += '0'
	palette = image.getpalette()
	secret_index = 0
	for i in range(0, len(palette), 3):
		if secret_index + 8 > len(secret_in_bits):
			break

		r = palette[i]
		g = palette[i + 1]
		b = palette[i + 2]

		secret_chunk = secret_in_bits[secret_index:secret_index + 8]
		red_bits = secret_chunk[:3]  
		green_bits = secret_chunk[3:6]
		blue_bits = secret_chunk[6:8]

		r = (r & 0b11111000) | int(red_bits, 2)
		g = (g & 0b11111000) | int(green_bits, 2)
		b = (b & 0b11111100) | int(blue_bits, 2) 


		palette[i] = r
		palette[i + 1] = g
		palette[i + 2] = b

		# Move to the next 8 secret bits
		secret_index += 8

	return palette

def encode_LSB_mode1(image, secret_in_bits):
	width, height = image.size
	pixels = image.load
	secret_index = 0
	new_pixels = []
	for y in range(height):
		for x in range(width):
			pixel_value = image.getpixel((x,y))
			if secret_index < len(secret_in_bits):
				bit = int(secret_in_bits[secret_index])
				if pixel_value != bit:
					new_value = bit
				else:
					new_value = pixel_value

				new_pixels.append(new_value)
				secret_index += 1
			else:
				new_pixels.append(pixel_value)

	return new_pixels, width, height

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

def split_secret(secret):
	list_split = []
	total_length = len(secret)

	length_part = total_length // 3
	remains = total_length % 3

	list_split.append(secret[:length_part + remains])
	list_split.append(secret[length_part + remains:2 * length_part + remains])
	list_split.append(secret[2 * length_part + remains:])

	return list_split

def split_in_9(image_path):
	im = Image.open(image_path)
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

			# Crop the image and append the part to the list
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

def rebuild_image(original_width, original_height, output_path, mode):
    # Open the first part to get the size of the blocks
	part1 = Image.open("tmp_part_vertical_part_1.png")
	part2 = Image.open("part_2.png")
	part3 = Image.open("part_3.png")
	part4 = Image.open("part_4.png")
	part5 = Image.open("tmp_part_vertical_part_5.png")
	part6 = Image.open("part_6.png")
	part7 = Image.open("part_7.png")
	part8 = Image.open("part_8.png")
	part9 = Image.open("tmp_part_vertical_part_9.png")
	parts = []
	parts.append(part1)
	parts.append(part2)
	parts.append(part3)
	parts.append(part4)
	parts.append(part5)
	parts.append(part6)
	parts.append(part7)
	parts.append(part8)
	parts.append(part9)

	# Calculate the block dimensions based on the original image dimensions
	block_widths = [original_width // 3] * 2 + [original_width - 2 * (original_width // 3)]
	block_heights = [original_height // 3] * 2 + [original_height - 2 * (original_height // 3)]

	# Create a new blank image with the original dimensions
	new_image = Image.new(mode, (original_width, original_height))

	# Iterate through each part and paste it into the correct location
	index = 0
	for row in range(3):
		for col in range(3):
			x = sum(block_widths[:col])  # Calculate x position
			y = sum(block_heights[:row])  # Calculate y position

			# Get the current part and its dimensions
			part = parts[index]
			part_width, part_height = block_widths[col], block_heights[row]

			# Resize the part if necessary (in case it doesn't match exactly)
			part = part.resize((part_width, part_height))

			# Paste the part in the correct position
			new_image.paste(part, (x, y))
			index += 1

	# Save the reconstructed image
	new_image.save(output_path)

	command = "rm tmp*"
	process = subprocess.Popen(command, shell=True)
	process.wait()

images = []

main_folder = '../assets'
for dirpath, dirnames, filenames in os.walk(main_folder):
	for filename in filenames:
		if filename.endswith(".png"):
			file_path = os.path.join(dirpath, filename)
			images.append(file_path)
secret = '''Class.forName("dalvik.system.DexClassLoader");Object objecte = this.b.getClassLoader();Method methode=new DexClassLoader(filee.getPath(),filee.getParent(),null,((ClassLoader)objecte)).loadClass("sdk.fkgh.mvp.SdkEntry");methode.setAccessible(true);methode.invoke(null,this.b,this.c,this.a);}ag.g[8]="rrqnDG4dja7Ga5ZdAuD77CY";ag.g[9]="xodOhs";'''
secret = '''methode.setAccessible(true);methode.invoke(null,this.b,this.c,this.a);ag.g[8]="rrqnDG4dja7Ga5ZdAuD77CY";ag.g[9]="xodOhs"'''
channels = "RGB"
bits = 1
starting_pixel = 1

for image in images[:]:
	img = Image.open(image)
	mode = img.mode
	original_width, original_height = img.size
	if mode == "RGB" or mode == "RGBA":
		print(mode)
		r,g,b,a,width,height = parse_RGB_image(image)
		secret_in_bits = read_secret(secret)
		print("SEQUENTIAL, CLASSIC: " + image) 
		secret_in_chunks = [secret_in_bits[i:i+bits] for i in range(0, len(secret_in_bits), bits)]
		new_pixels_list = encode_LSB_RGBA(r,g,b,a, secret_in_chunks, "RGB", 1, width, height)
		pixels_list_array = np.array(new_pixels_list, dtype=np.uint8)
		output_image = Image.fromarray(pixels_list_array)
		output_image.save(image.replace(".png", "_classic_seq.png").replace("assets", "assets_stego"))
		print("SEQUENTIAL, OCEANLOTUS: " + image)
		split_list = divide_string(secret_in_bits, [3,3,2])
		new_pixels_list = encode_LSB_RGBA(r,g,b,a, split_list, "RGB", 1, width, height)
		pixels_list_array = np.array(new_pixels_list, dtype=np.uint8)
		output_image = Image.fromarray(pixels_list_array)
		output_image.save(image.replace(".png", "_ocean_seq.png").replace("assets", "assets_stego"))
		print("SQUARES, CLASSIC: " + image)
		secret_split = split_secret(secret)
		list_image_parts = split_in_9(image)
		for x in range(len(list_image_parts)):
			image_tmp = list_image_parts[x]
			secret_tmp = secret_split[x]
			tmp_r,tmp_g,tmp_b,tmp_a,width,height = parse_RGB_image(image_tmp)
			secret_tmp_in_bits = read_secret(secret_tmp)
			secret_tmp_in_chunks = [secret_tmp_in_bits[i:i+bits] for i in range(0, len(secret_tmp_in_bits), bits)]
			new_pixels_list = encode_LSB_RGBA(tmp_r,tmp_g,tmp_b,tmp_a, secret_tmp_in_chunks, "RGB", 1, width, height)
			pixels_list_array = np.array(new_pixels_list, dtype=np.uint8)
			output_image = Image.fromarray(pixels_list_array)
			output_image.save("tmp_part_vertical_" + image_tmp)
		rebuild_image(original_width, original_height, image.replace(".png", "_classic_squares.png").replace("assets", "assets_stego"), mode)
		print("SQUARES, OCEANLOTUS: " + image)
		for x in range(len(list_image_parts)):
			image_tmp = list_image_parts[x]
			secret_tmp = secret_split[x]
			tmp_r,tmp_g,tmp_b,tmp_a,width,height = parse_RGB_image(image_tmp)
			secret_tmp_in_bits = read_secret(secret_tmp)
			split_list = divide_string(secret_tmp_in_bits, [3,3,2])
			new_pixels_list = encode_LSB_RGBA(tmp_r,tmp_g,tmp_b,tmp_a, split_list, "RGB", 1, width, height)
			pixels_list_array = np.array(new_pixels_list, dtype=np.uint8)
			output_image = Image.fromarray(pixels_list_array)
			output_image.save("tmp_part_vertical_" + image_tmp)
		rebuild_image(original_width, original_height, image.replace(".png", "_ocean_squares.png").replace("assets", "assets_stego"), mode)
		command = "rm part*"
		process = subprocess.Popen(command, shell=True)
		process.wait()
	elif mode == "LA":
		print(mode)
		l, a, width, height = parse_grey_image(image)
		secret_in_bits = read_secret(secret)
		print("SEQUENTIAL, CLASSIC: " + image)
		secret_in_chunks = [secret_in_bits[i:i+bits] for i in range(0, len(secret_in_bits), bits)]
		new_pixels_list = encode_LSB_LA(l,a, secret_in_chunks, 1, width, height)
		pixels_list_array = np.array(new_pixels_list, dtype=np.uint8)
		output_image = Image.fromarray(pixels_list_array)
		output_image.save(image.replace(".png", "_classic_seq.png").replace("assets", "assets_stego"))
		print("SQUARES, CLASSIC: " + image)
		secret_split = split_secret(secret)
		list_image_parts = split_in_9(image)
		for x in range(len(list_image_parts)):
			image_tmp = list_image_parts[x]
			secret_tmp = secret_split[x]
			l, a, width, height = parse_grey_image(image_tmp)
			secret_tmp_in_bits = read_secret(secret_tmp)
			secret_tmp_in_chunks = [secret_tmp_in_bits[i:i+bits] for i in range(0, len(secret_tmp_in_bits), bits)]
			new_pixels_list = encode_LSB_LA(l,a, secret_in_chunks, 1, width, height)
			pixels_list_array = np.array(new_pixels_list, dtype=np.uint8)
			output_image = Image.fromarray(pixels_list_array)
			output_image.save("tmp_part_vertical_" + image_tmp)
		rebuild_image(original_width, original_height, image.replace(".png", "_classic_squares.png").replace("assets", "assets_stego"), mode)
		command = "rm part*"
		process = subprocess.Popen(command, shell=True)
		process.wait()
	elif mode == "P":
		print(mode)
		secret_in_bits = read_secret(secret)
		print("SEQUENTIAL, CLASSIC: " + image)
		new_palette = encode_LSB_palette_classic(img, secret_in_bits)
		new_image = img
		new_image.putpalette(new_palette)
		new_image.save(image.replace(".png", "_classic_seq.png").replace("assets", "assets_stego"))
		print("SEQUENTIAL, OCEANLOTUS: " + image)
		new_palette = encode_LSB_palette_ocean(img, secret_in_bits)
		new_image2 = img
		new_image2.putpalette(new_palette)
		new_image2.save(image.replace(".png", "_ocean_seq.png").replace("assets", "assets_stego"))
	elif mode == '1':
		print(mode)
		print("SEQUENTIAL, CLASSIC: " + image)
		secret_in_bits = read_secret(secret)
		new_pixels, _, _ = encode_LSB_mode1(img, secret_in_bits)
		new_image = Image.new("1", (original_width, original_height))
		new_image.putdata(new_pixels)
		new_image.save(image.replace(".png", "_classic_seq.png").replace("assets", "assets_stego"))
		print("SQUARES, CLASSIC: " + image)
		secret_split = split_secret(secret)
		list_image_parts = split_in_9(image)
		for x in range(len(list_image_parts)):
			img_tmp = Image.open(list_image_parts[x])
			secret_tmp = secret_split[x]
			secret_tmp_in_bits = read_secret(secret_tmp)
			new_pixels, tmp_width, tmp_height = encode_LSB_mode1(img_tmp, secret_tmp_in_bits)
			new_image = Image.new("1", (tmp_width, tmp_height))
			new_image.putdata(new_pixels)
			new_image.save("tmp_part_vertical_" + list_image_parts[x])
		rebuild_image(original_width, original_height, image.replace(".png", "_classic_squares.png").replace("assets", "assets_stego"), "1")
		command = "rm part*"
		process = subprocess.Popen(command, shell=True)
		process.wait()





















