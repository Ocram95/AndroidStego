from PIL import Image
import numpy as np
import sys
import optparse


def process_command_line(argv):
	parser = optparse.OptionParser()
	parser.add_option('-i', '--input', help='Specify the input image.', action='store', type='string', dest='input')
	parser.add_option('-s', '--secret', help='Specify the secret to imbed in the input image.', action='store', type='string', dest='secret')
	parser.add_option('-c', '--channels', help='Specify the number of channels to use.', action='store', type='string', dest='channels', default='RGB')
	parser.add_option('-b', '--bits', help='Specify the number of bits per channel to use.', action='store', type='int', dest='bits', default=1)
	parser.add_option('-p', '--pixel', help='Specify the starting pixel.', action='store', type='int', dest='starting_pixel', default=1)

	settings, args = parser.parse_args(argv)
	return settings, args

def parse_image(image_path):
	with Image.open(image_path) as im:
		#it returns RGB or RGBA (if alpha channel is present)
		mode = im.mode
		#alpha channel
		a = []
		if len(mode) == 3:
			r,g,b = im.split()
			alpha = []
		else:
			r,g,b, a = im.split()
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

def decode_sequential(r, g, b, bits, channels, pixel_index):
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

def read_secret(secret_path):
	secret_in_bits = ''.join(format(ord(bit), '08b') for bit in secret_path)
	return secret_in_bits

def secret_correctly_encoded(secret_in_chunks, output):
	for x in range(len(secret_in_chunks)):
		#check if the x-th element of the secret injected is equal to the one extracted
		if(secret_in_chunks[x] != output[x]):
			#sometimes it is possible that the secret injected can be something like 
			#['000', '010', '10'], i.e., the last element is different in terms of size w.r.t.
			#the other elements. Thus, the following check deals with this situations.
			if secret_in_chunks[x] != output[x][-len(secret_in_chunks[x]):]:
				return False
	return True

def divide_stringa(stringa, lunghezze):
	lista_divisa = []

	indice_inizio = 0
	while indice_inizio < len(stringa):
		for lunghezza in lunghezze:
			sottostringa = stringa[indice_inizio:indice_inizio + lunghezza]
			lista_divisa.append(sottostringa)
			indice_inizio += lunghezza

	return lista_divisa

def decode_OceanLotus(r, g, b, bits, channels, pixel_index):
	extracted_secret_in_bits = []
	for x in range(len(r)):
		if x >= pixel_index - 1:
			if "R" in channels:
				extracted_secret_in_bits.append(r[x][-bits[0]:])
			if "G" in channels:
				extracted_secret_in_bits.append(g[x][-bits[1]:])
			if "B" in channels:
				extracted_secret_in_bits.append(b[x][-bits[2]:])
	return extracted_secret_in_bits

def raggruppa_e_converti(lista_di_bit):
	caratteri_ascii = []

	# Unisci tutti gli elementi della lista in una singola stringa
	stringa_di_bit = ''.join(lista_di_bit)

	# Dividi la stringa in gruppi di 8 bit
	gruppi_di_8_bit = [stringa_di_bit[i:i+8] for i in range(0, len(stringa_di_bit), 8)]

	# Converti ciascun gruppo di 8 bit in un carattere ASCII
	for gruppo_di_8_bit in gruppi_di_8_bit:
		carattere_ascii = chr(int(gruppo_di_8_bit, 2))
		caratteri_ascii.append(carattere_ascii)

	return caratteri_ascii

##### LSB NORMAL
# settings, args = process_command_line(sys.argv)
# secret_in_bits = read_secret(settings.secret)
# secret_in_chunks = [secret_in_bits[i:i+settings.bits] for i in range(0, len(secret_in_bits), settings.bits)]
# r,g,b,a, width, height = parse_image(settings.input)
# output = decode_sequential(r,g,b, settings.bits, settings.channels, settings.starting_pixel)

# success = secret_correctly_encoded(secret_in_chunks, output)
# if success:
# 	print("Secret correctly decoded!")
# 	final_secret = (raggruppa_e_converti(output[:len(secret_in_bits)]))
# 	secret_extracted = ''.join(final_secret)
# 	print(secret_extracted)
# else:
# 	print(str(settings.input))
# 	print("ERROR!")
# 	sys.exit()


############## OCEANLOTUS
settings, args = process_command_line(sys.argv)
secret_in_bits = read_secret(settings.secret)
r,g,b,a, width, height = parse_image(settings.input)
test = divide_stringa(secret_in_bits, [3,3,2])
output = decode_OceanLotus(r,g,b, [3,3,2], settings.channels, settings.starting_pixel)

# a1 = raggruppa_e_converti(output)
# stringa_unita = ''.join(a1)
# print(settings.input)
# print(stringa_unita[:100])

success = secret_correctly_encoded(test, output)
if success:
	print("Secret correctly decoded! " + str(settings.input))
else:
	print(str(settings.input))
	print("ERROR!")
	sys.exit()

