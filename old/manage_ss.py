#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket, sys, os

import json
from pprint import pprint
import random
from xkcdpass import xkcd_password as xp


class ShadowSocksManager():

	def __init__(self, domain_socket):


		self.SOCKET_BUFFER_SIZE = 4096
		self.sock = None

		self.sock_address = domain_socket

		if not os.path.exists( domain_socket ):
			raise ValueError( "socket %s did not exist." % self.sock_address )

		# Datagram (udp) socket
		try :
			self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

			self.sock.bind('/tmp/client-ssm.sock')  # address of the client
			print("Bound to client socket /tmp/client.sock")

			self.sock.connect( self.sock_address )
			print("Connected to socket", self.sock_address, '.' )

			print( 'Socket created.' )

		except socket.error as err:
			print('Failed to create socket. Error:', str(err) )
			sys.exit()



	def mylist(self):
		'''returns the list of all ports and their bandwidth usage.'''

		#sig_ping = bytes('ping\n', 'utf-8')

		self.sock.send( b'ping' )
		#self.sock.send( b'ping\n', self.sock_address )

		z = self.sock.recv(1506)  # You'll receive 'pong'

		return z


		#return self.myrecv()


	def myrecv(self):
		#data = self.sock.recvfrom( self.SOCKET_BUFFER_SIZE )
		data = self.sock.recv(1506)
		z = repr(data)

		print("got back:", z )
		return z




if __name__ == '__main__':

	DOMAIN_SOCKET = '/tmp/manager.sock'

	SS = ShadowSocksManager( DOMAIN_SOCKET )

	print("We connected.")

	print("doing ss.mylist()")

	pprint( SS.mylist() )
