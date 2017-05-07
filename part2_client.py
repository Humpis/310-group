#!/usr/bin/python

import socket
import sys

def info_send(socket):
	#Sends the global send variable out on the socket fed into the variable socket.
	#If it cannot send it out, it will assume the connection is closed and exit the
	#program after displaying an error.
	global glob_message_send
	try:
		socket.send(glob_message_send.encode())
	except:
		print('Uh oh! Something went wrong! Did the server shut down?')
		exit()
	return 1

def info_decode(info):
	#Will take info, usually obtained from the server via a connection socket,
	#decode it, and split it across the hash characters, storing the list within
	#the global receive variable. If it cannot, it assumes the server has sent a
	#malformed response and will shut down the connection and exit.
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
	#Will take a gameID and attempt to connect to that ID on the server. Will send out a
	#200 Join Game request. Will return -1 if it receives a 408 Join Error. If it receives
	#a 201 Join ACK, it will wait for a 213 Gamestate response to signal the game has started.
	#Once a 213 message is recieved, it will return 1. Will return -1 if a message other than
	#408 or 213 is recieved.
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
	if glob_message_recv[0] == 408:
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
	#Displays all the commands the client supports, their syntax, and what their expected
	#outputs are.
	print ("help: displays a list of commands, their syntax and their expected results")
	print ("place #: places an X/O at location 1,2,3 4,5,6 7,8,9 on the game board")
	print ("exit: leaves your current game and exits the server.")
	print ("games: queries the server for a list of all active games. (game_id,player_x,player_o)")
	print ("who: queries the server for a list of all logged-in players and their status. (user_id,status)")
	print ("play <game_id>: tell the server you would wish to join a specified lobby.")

def print_query(query):
	#Will take in a string, usually the payload of a 131 or 132 Response, and display its
	#semi-colon separated list line by line.
	query = query.split(';')
	x = 0
	while x < len(query):
		print(query[x])
		x += 1

def quit_server():
	#Will send a 110 Logout Notification to the server. After which, it will close
	#the socket used for transmission.
	global glob_message_send
	global client_socket
	
	print('Closing connection to server...')
	glob_message_send = "110#"+glob_uid
	info_send(client_socket)
	
	client_socket.close()

def display_gamestate(gamestate):
	#Takes a string at least 10 characters long, usually obtained via a 213 Gamestate
	#message, and displays a tic-tac-toe board using them.
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

def take_input(status):
	#Waits for player to enter any of the commands supported by the client. Returns a 
	#struct indicating command executed and its related data. Status indicates the menu
	#where input is being taken. 0 is in lobby,	1 is in game. Queries performed
	#while in game will refer to the local query listings rather than making
	#new queries to the server.
	#Return 1 -> Place; Return 2 -> Quit; Return 3 -> Query; Return 4 -> Play;
	
	global glob_players
	global glob_games
	
	while (1):
		uinput = input('# ')
		if uinput == 'help':
			print_help()
			continue
		if uinput.startswith('place '):
			if status == 1:
				try:
					uinput = int(uinput[5:])
					if uinput < 1 or uinput > 9:
						print ('Invalid move: Invalid location')
						continue
					return (1, uinput)
				except ValueError:
					print ('Invalid input for place command. Type help to see syntax.')
			else:
				print ("You currently aren't in a game.")
		if uinput == 'exit':
			return (2,)
		if uinput == 'games':
			if status == 1:
				print_query(glob_games)
			else:
				return (3,0)
		if uinput == 'who':
			if status == 1:
				print_query(glob_players)
			else:
				return (3,1)
		if uinput.startswith('play '):
			if status == 1:
				print ("You can't start another game until you finish this one!")
				continue
			else:
				try:
					uinput = int(uinput[5:])
					return (4, uinput)
				except ValueError:
					print ('Invalid input for play command. Type help to see syntax.')

def play_game(rcv_msg):
	#The game loop for the tic_tac_toe game. rcv_msg is the first 213 gamestate message
	#that signifies the game is ready to be played.
	#Loop operation is as follows:
	##Will display current gamestate, will check if it is user's turn by comparing
	##global userID to the current turen userID specified in the 213 gamestate message.
	##If it isn't the user's turn, the client will wait for a 213 Gamestate or a
	##214 Game Result. If it is the user's turn it will call take_input and use that
	##to determine whether to place (uinput[0] == 1) or quit (uinput[0] == 2)
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
			uinput = take_input(1)
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
				print('Exiting game...')
				glob_message_send = "204#"+glob_uid+"#"+str(glob_gameid)
				info_send(client_socket)
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

#End of method definitions

#Start of significant and global variable definition
server_name = sys.argv[1]
server_port = int(sys.argv[2])
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

glob_message_send = '100#noname'
glob_message_recv = '499#UNEXECUTED#UNEXECTUED'
glob_error = "CODE HASN'T BEEN EXECUTED"
glob_uid = 'noname'
glob_gameid = 0
glob_players = 'server,0000;'
glob_games = '0001,server,server;'
#End of significant and global variable definition

##Start of program operation
#Establish connection with server
try:
	client_socket.connect((server_name,server_port))
except:
	print('Error connecting to server. Is it online?')
	exit()
while (1):
	
	#Grab username from user and send it to the server
	client_username = input('Enter your username: ')
	#Prevents use of special characters that would interfere with message transmission
	#in the use of usernames.
	if '#' in client_username or ';' in client_username or ',' in client_username:
		print ('Invalid username. Remove special characters (#,;) and try again.')
		continue
	glob_message_send = '100#'+ client_username
	info_send(client_socket)
	info = client_socket.recv(1024)
	info_decode(info)
	uname_ack_code = glob_message_recv[0]
	
	#Check for 101 Username ACK or 401 Login Denied
	if uname_ack_code == 101:
		glob_uid = glob_message_recv[1]
		print('You are now connected to ' + server_name + ' as ' + glob_uid)
		break
	elif uname_ack_code == 401:
		print (glob_message_recv[1])
	else:
		print ('Unexpected Issue. Please try again.')

#Main Lobby Loop. This will take user input when user isn't in game. From here
#user can, quit (uinput[0] == 2), send a query (uinput[0] == 3), or join a 
#game (uinput[0] == 4).
while (1):
	uinput = take_input(0)
	if uinput[0] == 2:
		#Quit
		quit_server()
		exit()
	if uinput[0] == 3:
		if uinput[1] == 0:
			#Send Game Query
			glob_message_send = '130#'+glob_uid+'#2'
		if uinput[1] == 1:
			#Send Player Query
			glob_message_send = '130#'+glob_uid+'#1'
		info_send(client_socket)
		info = client_socket.recv(1024)
		code = info_decode(info)
		if code == 131:
			glob_players = glob_message_recv[1]
			print ('Player Listing')
			print ('==============')
			print_query(glob_players)
		elif code == 132:
			glob_games = glob_message_recv[1]
			print ('Game Listing')
			print ('============')
			print_query(glob_games)
	if uinput[0] == 4:
		print ('Joining Game')
		game_status = join_game(uinput[1])
		if game_status == 1:
			print ('Joined Game!')
			play_game(glob_message_recv)
		else:
			print ("Game is full or doesn't exist.")

print ('Thats all for now!')