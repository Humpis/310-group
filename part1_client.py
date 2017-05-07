#!/usr/bin/python

import socket
import sys
import re

def server_connect(location, port):
	##TODO
	return 0
def info_send(socket):
	global glob_message_send
	try:
		socket.sendall(glob_message_send.encode())
	except:
		print('Uh oh! Something went wrong! Did the server shut down?')
		exit()
	return 1
def info_decode(info):
	global glob_message_recv
	try:
		glob_message_recv = info.decode().split('#')
		glob_message_recv[0] = int(glob_message_recv[0])
		code = glob_message_recv[0]
	except:
		print('Uh oh! The server you are connected too seems to be experiencing an unexpected error')
		try:
			quit_server()
			exit()
		except:
			exit()
	return code
def join_game(gid):
	global glob_message_send
	global glob_uid
	global client_socket
	global glob_message_recv
	game_status = -1
	
	glob_message_send = '200#' + str(glob_uid) + '#' + str(gid)
	info_send(client_socket)
	info = client_socket.recv(1024)
	info_decode(info)
	
	#Check to see if game is full
	if glob_message_recv[0] == 400:
		game_status = -1
	elif glob_message_recv[0] == 201:
		game_status = 1
		
	if game_status == -1:
		return -1
	else:
		while (1):
			print ('Waiting for game to begin...')
			info = client_socket.recv(1024)
			info_decode(info)
			#print (glob_message_recv) ##DEBUG
			if glob_message_recv[0] == 213:
				return 1
def print_help():
	print ("help: displays a list of commands, their syntax and their expected results")
	print ("place #: places an X/O at location 1,2,3 4,5,6 7,8,9 on the game board")
	print ("exit: leaves your current game and exits the server.")
def quit_server():
	global glob_message_send
	global glob_gameid
	global client_socket
	
	print('Exiting game...')
	glob_message_send = "204#"+glob_uid+"#"+str(glob_gameid)
	info_send(client_socket)
	
	print('Closing connection to server...')
	glob_message_send = "110#"+glob_uid
	info_send(client_socket)
	
	client_socket.close()
def display_gamestate(gamestate):
	gamestate.replace('_', ' ')
	board = list(gamestate)
	#print (gamestate) ##DEBUG
	#print (board) ##DEBUG
	print('   |   |')
	print(' ' + board[1] + ' | ' + board[2] + ' | ' + board[3])
	print('   |   |')
	print('-----------')
	print('   |   |')
	print(' ' + board[4] + ' | ' + board[5] + ' | ' + board[6])
	print('   |   |')
	print('-----------')
	print('   |   |')
	print(' ' + board[7] + ' | ' + board[8] + ' | ' + board[9])
	print('   |   |')
def take_input():
	#Waits for player to enter any of the commands. Returns a struct indicating command executed
	#and its related data.
	
	while (1):
		uinput = input('# ')
		if uinput == 'help':
			print_help()
			continue
		if uinput.startswith('place '):
			uinput = int(uinput[5:])
			if uinput < 1 or uinput > 9:
				print ('Invalid move: Invalid location')
				continue
			return (1, uinput)
		if uinput == 'exit':
			return (2,)
def play_game(rcv_msg):
	#The game loop for the tic_tac_toe game.
	global glob_uid
	global client_socket
	global glob_message_recv
	global glob_message_send
	global glob_gameid
	turn = -1
	uinput = -1
	glob_gameid = int(rcv_msg[1])
	boardstate = rcv_msg[2]
	
	while (1):
		display_gamestate(boardstate)
		if rcv_msg[3] == glob_uid:
		#Grabs the user turn from the server's message, determining if it is the client's turn or
		#not.
			turn = 1
			print ("It's your turn!")
			uinput = take_input()
			if uinput[0] == 1:
				if boardstate[int(uinput[1])] == ' ':
					glob_message_send = "210#"+glob_uid+"#"+str(glob_gameid)+"#"+str(uinput[1])
					#print (glob_message_send) ##DEBUG
					info_send(client_socket)
					info = client_socket.recv(1024)
					info_decode(info)
					if glob_message_recv[0] == 211:
						#Place ACK recieved. Sending gamestate query
						glob_message_send = "212#"+glob_uid+"#"+str(glob_gameid)
						info_send(client_socket)
						info = client_socket.recv(1024)
						info_decode(info)
						rcv_msg = glob_message_recv
						boardstate = rcv_msg[2]
					elif glob_message_recv[0] == 214:
						print (glob_message_recv[2])
						break
					else:
						#Placement Error
						print ('Placement Error')
				else:
					print ('Invalid move: Space already occupied.')
			elif uinput[0] == 2:
				#Quit game and exit program
				quit_server()
				exit()
		else:
			turn = -1
			print ("It's your opponent's turn. Please wait...")
			info = client_socket.recv(1024)
			info_decode(info)
			if glob_message_recv[0] == 213:
				rcv_msg = glob_message_recv
				boardstate = rcv_msg[2]
			elif glob_message_recv[0] == 214:
				print (glob_message_recv[2])
				break

server_name = sys.argv[1]
server_port = int(sys.argv[2])
tmp_game_id = int(sys.argv[3])
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

glob_message_send = '100#noname'
glob_message_recv = '499#UNEXECUTED#UNEXECTUED'
glob_error = "CODE HASN'T BEEN EXECUTED"
glob_uid = 'noname'
glob_gameid = 0
#End of significant variable definiton

##Establish connection with server
try:
	client_socket.connect((server_name,server_port))
except:
	print('Error connecting to server. Is it online?')
	exit()
while (1):
	
	#Grab username from user and send it to the server
	client_username = input('Enter your username: ')
	glob_message_send = '100#'+ client_username
	info_send(client_socket)
	info = client_socket.recv(1024)
	info_decode(info)
	uname_ack_code = glob_message_recv[0]
	
	#Check for 101 Username ACK or 400 Username Taken
	if uname_ack_code == 101:
		glob_uid = glob_message_recv[1]
		print('You are now connected to ' + server_name + ' as ' + glob_uid)
		break
	elif uname_ack_code == 400:
		print (glob_message_recv[1])
	else:
		print ('Unexpected Issue. Please try again.')

##Main Program Loop
glob_gameid = tmp_game_id
while (1):
	
	##Join Game 0001
	#Part 1 Auto Join's game 0001
	print ('Joining Game')
	game_status = join_game(glob_gameid)
	if game_status == 1:
		print ('SUCCESS!')
		play_game(glob_message_recv)
	else:
		print ('Game is full.')
		exit()
	glob_gameid += 1
	

print ('Thats all for now!')