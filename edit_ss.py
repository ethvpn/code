#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket, sys, os

import json
from pprint import pprint
import random
from xkcdpass import xkcd_password as xp


class ShadowSocksManager():

	def __init__(self, server_socket, client_socket):


		self.MIN_PORT_NUMBER, self.MAX_PORT_NUMBER = 1024, 2048
		self.MAX_PASSWORD_LENGTH = 28
		self.PASSWORD_NUMBER_OF_WORDS = 3

		#self.SOCKET_BUFFER_SIZE = 1506
		self.SOCKET_BUFFER_SIZE = 4096

		self.xkcd_wordfile = xp.locate_wordfile()
		self.xkcd_wordlist = xp.generate_wordlist(wordfile=self.xkcd_wordfile, max_length=5)

		# keep track of all of the ports currently in use
		self.ports_in_use = set([])
		self.data_used = dict([])

		self.sock = None

		self.server_address = server_socket
		self.client_address = client_socket

		if not os.path.exists( self.server_address ):
			raise ValueError( "server socket %s did not exist." % self.server_address )

		if os.path.exists( self.client_address ):
			raise ValueError( "client socket %s already exists." % self.client_address )

		# Datagram (udp) socket
		try :
			self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
			print( 'Socket created.' )

			self.sock.bind( self.client_address )
			print("Bound client to socket", self.client_address, '.' )


			self.sock.connect( self.server_address )
			print("Connected to socket", self.server_address, '.' )


		except socket.error as err:
			print('Failed to create socket. Error Code : ' + str(err[0]) + ' Message ' + err[1] )
			sys.exit()


	def __del__(self):
		'''I don't think using __del__ is considered correct style, but I didn't see any other way to do a destructor.'''

		# delete the client socket address
		if os.path.exists( self.client_address ):
			os.unlink( self.client_address )



	def recv(self):

		z = self.sock.recv( self.SOCKET_BUFFER_SIZE )

		z = str(z,'utf-8').strip()

		# if we got back a python data-structure, return that.

		# remove anything before a ':'
		if z.startswith('stat:'):
			z = (z[ z.index(':') +1 : ]).strip()

			# strip any single quotes from the edges
			z = z.strip("'")

			z = json.loads(z)


			# keep track of all of the ports currently in use
			if type(z) is dict:
				self.ports_in_use |= set( [ int(x) for x in list(z.keys()) ] )
				self.data_used = z

				print("Got back refreshed ports-list:")
				pprint(z)


			#pprint(z)
			#print("type(z)=", type(z) )

		#z = repr(data)
		else:
			print("got back string:", z )

		return z


	def ls(self):
		'''returns the list of all ports and their bandwidth usage.'''

		self.sock.send( b'ping' )
		self.sock.send( b'ping\n' )
		
		return self.recv()



	def remove( self, port_number ):

		if type(port_number) is int:
			port_number = str(port_number)

		if not port_number.isdigit():
			raise ValueError("passed port_number wasn't a digit.")


		print("Used ports:", self.ports_in_use )

		if int(port_number) not in self.ports_in_use:
			raise ValueError("passed port_number %s isn't a used port." % port_number )

		

		# send these to the server
		the_str = 'remove: {"server_port": %s}' % port_number
		self.sock.send( bytes(the_str,'utf-8') )

		return self.recv()

	def generate(self):
		'''add new port/password to the system.'''

		###############################################################################
		# 1. generate the new port
		###############################################################################

		#current_ports = self.used_ports()
		current_ports = set([])

		possible_ports = set(range(self.MIN_PORT_NUMBER, self.MAX_PORT_NUMBER+1)) - current_ports

		if not possible_ports:
			raise ValueError("Didn't have any ports to choose from!")

		# could also do
		## new_port = possible_ports.pop()
		# but I was concerned that would make the port number too predictable
		new_port = int( random.choice( list(possible_ports) ) )

		###############################################################################
		# 2. generate the new password
		###############################################################################
		new_password = xp.generate_xkcdpassword( self.xkcd_wordlist, numwords=self.PASSWORD_NUMBER_OF_WORDS, delimiter='_' )


		# send these to the server
		the_str = 'add: {"server_port": %d, "password":"%s"}' % (new_port, new_password)
		self.sock.send( bytes(the_str, 'utf-8') )

		# add this to the use ports list
		self.ports_in_use.add( int(new_port) )


		return new_port, str(new_password)



if __name__ == '__main__':

	DOMAIN_SOCKET = '/var/run/ss-manager.sock'
	CLIENT_SOCKET = '/var/run/ss-client.sock'

	SS = ShadowSocksManager( DOMAIN_SOCKET, CLIENT_SOCKET )

	print("We connected.")

	print("doing ss.ls()")

	pprint( SS.ls() )


	print("Generating new port/password")
	newport1, newpass1 = SS.generate()
	print("Added port:", newport1, "\t", "password:", newpass1)

	newport2, newpass2 = SS.generate()
	print("Added port:", newport2, "\t", "password:", newpass2)


	print("doing ss.ls()")
	pprint( SS.ls() )

	print("Removing the first port:", newport1)
	SS.remove( newport1 )

	print("doing ss.ls()")
	pprint( SS.ls() )

