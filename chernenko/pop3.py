#coding: utf-8

import socket as sck
import sys
import base64
import ssl
import email
import logging
logging.basicConfig(level = logging.DEBUG)


class POP3:	

	def __init__(self, server_name, port):
		self.connect(server_name, port)			
		self.use_secure = False

	def connect(self, server_name, port):
		self.socket = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
		if port != 110:
			self.socket = ssl.wrap_socket(self.socket, ssl_version = ssl.PROTOCOL_SSLv23)
			self.use_secure = True
		logging.debug('before connect')
		logging.debug(server_name + ' ' + str(port))
		self.socket.connect((server_name, port))		
		logging.info('reply: ' + self.socket.recv(200))
		logging.debug('connected')

	def sendCommand(self, cmd, body = ''):		
		single_cmds = 'STAT', 'RSET', 'QUIT', 'NOOP'
		
		for cmd_single in single_cmds:
			if cmd == cmd_single:		
				break
		else:
			body = ' ' + body

		self.socket.send(cmd + body + '\r\n')
		logging.debug(cmd + body + ' cmd sent')							
		reply = self.socket.recv(200)		
		logging.debug('reply: ' + reply)
		return reply

	def getMessageSize(self, index):
		reply = self.sendCommand('LIST', str(index) + '\r\n')
		tokens = reply.split()
		if tokens[0] != '+OK':
			raise Exception('Something went wrong. Try later')
		return int(tokens[2])

	def copyContent(self, key_word, original, stop_word = '\r\n'):
		start = original.find(key_word)		
		end = original.find(stop_word, start)		
		return original[start:end]

	def parseHeader(self, header):
		result = []
		result.append(self.copyContent('Date:', header))
		result.append(self.copyContent('From:', header))
		result.append(self.copyContent('Subject:', header))
		result = '\r\n'.join(result)
		return result

	def getBigReply(self):
		reply = []
		while True:
			buf = self.socket.recv(1024)
			reply.append(buf)
			if buf.endswith('\r\n.\r\n'):
				break
		reply = ''.join(reply)
		if reply[:3] != '+OK':				
			raise Exception('This pop3 server is unsupported') #TODO
		return reply

	def recieveText(self, index):
		self.socket.send('TOP ' + str(index) + ' 0' + '\r\n')
		logging.debug('TOP ' + str(index) + ' 0' + ' cmd sent')
		reply = self.getBigReply()
		header = reply[:len(reply) - 3]		
		
		self.socket.send('RETR ' + str(index) + '\r\n')
		logging.debug('RETR ' + str(index) + ' cmd sent')
		reply = self.getBigReply()
		msg = reply[len(header):len(reply) - 3]
		print msg


	def simpleAuth(self, username, password):
		self.sendCommand('USER', username)
		self.sendCommand('PASS', password)
		self.sendCommand('STAT')

		self.recieveText(1)
		self.sendCommand('QUIT')

	def recieveMessages(self, username, password):
		if self.use_secure:
			self.secureAuth(username, password)
		else:
			self.simpleAuth(username, password)



if __name__ == '__main__':
	pop3 = POP3(sys.argv[1], int(sys.argv[2]))
	pop3.recieveMessages(sys.argv[3], sys.argv[4])