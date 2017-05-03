#!/usr/bin/python

import socket
import sys

def server_connect(location, port):
	##TODO
	return 0
def info_send(socket):
	global glob_message_send
	socket.send(glob_message_send.encode())
	return 1
def info_decode(info):
	#print info ##DEBUG
	global glob_message_recv
	glob_message_recv = info.split('#')
	glob_message_recv[0] = int(glob_message_recv[0])
	code = glob_message_recv[0]
	##TODO : Define handling for seperate codes
	return code
def join_game(gid):
	global glob_message_send
	global glob_uid
	global client_socket
	
	glob_message_send = '200#' + str(glob_uid) + '#' + str(gid)
	info_send(client_socket)
	info = client_socket.recv(1024)
	info_decode(info)
	
def return_100(message_parts):
	##TODO
	return 0
def return_200(message_parts):
	##TODO
	return 0
def return_400(message_parts):
	##TODO
	return 0

#End of method definitions
server_name = sys.argv[1]
server_port = int(sys.argv[2])
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

glob_message_send = '100#noname'
glob_message_recv = '499#UNEXECUTED#UNEXECTUED'
glob_error = "CODE HASN'T BEEN EXECUTED"
glob_uid = 9999
glob_username = 'noname'
#End of significant variable definiton

##Establish connection with server
try:
	client_socket.connect((server_name,server_port))
except:
	print 'Error connecting to server. Is it online?'
	exit()
while (1):
	#Grab username from user and send it to the server
	client_username = raw_input('Enter your username: ')
	glob_message_send = '100#'+ client_username
	info_send(client_socket)
	info = client_socket.recv(1024)
	info_decode(info)
	uname_ack_code = glob_message_recv[0]
	
	#Check for 101 Username ACK or 400 Username Taken
	if uname_ack_code == 101:
		##TODO: Grab UID and store in global var
		glob_username = glob_message_recv[1]
		glob_uid = glob_message_recv[2]
		print 'You are now connected to ' + server_name + ' as ' + glob_username + '(' + glob_uid + ')'
		break
	elif uname_ack_code == 400:
		print glob_message_recv[1]
	else:
		print 'Unexpected Issue. Please try again.'
##Join Game 0001
#Part 1 Auto Join's game 0001
join_game('0001')
info = client_socket.recv(1024)
info_decode(info)
print glob_message_recv[0]

print 'Thats all for now!'