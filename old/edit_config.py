#!/usr/bin/env python3
########################################################################
# This regenerates the config file for the shadowsocks server
########################################################################

# CONFIGRUABLE PARAMETERS
########################################################################

INCOMING_CONFIG_FILENAME = 'config.in.json'
OUTPUT_CONFIG_FILENAME = 'config.out.json'

MIN_PORT_NUMBER, MAX_PORT_NUMBER = 1024, 2048
MAX_PASSWORD_LENGTH = 28

# if don't want to change the values for these in INCOMING_CONFIG_FILE set to None
FORCE_ENCRYPTION_METHOD = 'aes-128-cfb'
FORCE_TIMEOUT_VALUE = 600

########################################################################
import json
import argparse
import os, sys
from pprint import pprint
import random
from xkcdpass import xkcd_password as xp
########################################################################
########################################################################
def read_config( INPUT_FILENAME ):

	assert os.path.isfile( INPUT_FILENAME ), "input file %s was not a file"

	with open(INPUT_FILENAME,'r') as f:
		d = json.load(f)

	#print("Readin config file:")
	#pprint(d)

	assert 'method' in d
	assert 'timeout' in d
	assert 'port_password' in d

	return d

def write_config( d, OUTPUT_FILENAME ):
	assert 'method' in d
	assert 'timeout' in d
	assert 'port_password' in d

	# checking the types
	assert type(d['timeout']) is int
	assert type(d['method']) is str
	assert type(d['port_password']) is dict

	# checking the values
	assert d['method'] in ('aes-128-ctr','aes-192-ctr','aes-256-ctr','chacha20-ietf','chacha20','salsa20','aes-128-cfb','aes-256-cfb')
	assert d['timeout'] > 0


	for key, value in d['port_password'].items():

		assert type(key) is str, "All keys be strings"		
		assert type(value) is str, "All passwords must be strings"

		assert key.isdigit(), "specified port wasn't a digit"
		assert len(value) <= MAX_PASSWORD_LENGTH, "Password was too long"




	with open(OUTPUT_FILENAME, 'w') as f:
		#pprint(d)
		json.dump(d, f, indent=True, sort_keys=True)

		#print("Wrote config file:")
		#pprint(d)

def generate_new_port_password_pair( current_ports ):
	global MIN_PORT_NUMBER, MIN_PORT_NUMBER
	global MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH

	###############################################################################
	# 1. generate the new port
	###############################################################################

	possible_ports = set(range(MIN_PORT_NUMBER, MAX_PORT_NUMBER+1)) - set(current_ports)

	if not possible_ports:
		raise ValueError("Didn't have any ports to choose from!")

	# could also do
	## new_port = possible_ports.pop()
	# but I was concerned that would make the port number too predictable

	new_port = random.choice( list(possible_ports) )


	###############################################################################
	# 2. generate the new password
	###############################################################################
	xkcd_wordfile = xp.locate_wordfile()
	xkcd_wordlist = xp.generate_wordlist(wordfile=xkcd_wordfile, max_length=5)
	new_password = xp.generate_xkcdpassword(xkcd_wordlist, numwords=4, delimiter='-')
	#new_password = xp.generate_xkcdpassword(xkcd_wordlist, acrostic="ethvpn")	


	return str(new_port), str(new_password)


if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Add/removes ports+passwords pairs from the shadowsocks config file.', epilog='This is my epilog.')
	parser.add_argument('-g', '--gen', action='store_true', default=False, help='generate a single new port/password pair')
	parser.add_argument('-d', '--delete', nargs='+', action='append', help='delete the accounts associated with these ports')
	parser.add_argument('--version', action='version', version='%(prog)s 0.1')

	args = parser.parse_args()

#	pprint(args)

	if args.delete is None and args.gen is False:
		parser.print_help()
		sys.exit(0)

	if args.delete is not None:
		assert len(args.delete) == 1, "This should always be a list of length 1"
		args.delete = args.delete[0]


	# 1. readin the current config file
	d = read_config( INCOMING_CONFIG_FILENAME )


	if FORCE_ENCRYPTION_METHOD:
		d['method'] = FORCE_ENCRYPTION_METHOD

	if FORCE_TIMEOUT_VALUE:
		d['timeout'] = FORCE_TIMEOUT_VALUE
 


	# 2. Delete any ports/passwords, if we're doing that.
	if args.delete:
		#pprint(args.delete)
		for x in args.delete:
			if x not in d['port_password']:
				print("Warning: port '%s' was not in the accounts list.  Skipping." % x, file=sys.stderr)
				continue

			del d['port_password'][x]


	# generate a new port/passsword, if we're doing that.
	if args.gen:
		current_ports = list(d['port_password'].keys())
		#pprint(current_ports)
		new_port, new_password = generate_new_port_password_pair( current_ports )

		assert new_port not in d['port_password']

		d['port_password'][str(new_port)] = new_password

		
		# printing the new password
		print( json.dumps( { 'port': new_port, 'password': new_password }, sort_keys=True) )



	# write the new config file
	write_config(d, OUTPUT_CONFIG_FILENAME )

