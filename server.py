import os
import sys
import errno
import select
import socket
import optparse

BACKLOG = 5

games = []

def drawBoard(board):
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

def makeMove(board, letter, move):
    board[move] = letter

def isWinner(bo, le):
    return ((bo[7] == le and bo[8] == le and bo[9] == le) or
    (bo[4] == le and bo[5] == le and bo[6] == le) or
    (bo[1] == le and bo[2] == le and bo[3] == le) or
    (bo[7] == le and bo[4] == le and bo[1] == le) or
    (bo[8] == le and bo[5] == le and bo[2] == le) or
    (bo[9] == le and bo[6] == le and bo[3] == le) or
    (bo[7] == le and bo[5] == le and bo[3] == le) or
    (bo[9] == le and bo[5] == le and bo[1] == le))

def isSpaceFree(board, move):
    return board[move] == ' '

def getPlayerMove(board):
    move = ' '
    while move not in '1 2 3 4 5 6 7 8 9'.split() or not isSpaceFree(board, int(move)):
        move = input()
    return int(move)

def isBoardFull(board):
    for i in range(1, 10):
        if isSpaceFree(board, i):
            return False
    return True

def newgame(gameId, X, O):
    games[gameid]['board'] = [' '] * 10
    games[gameid]['turn'] = 'X'
    games[gameid]['isPlaying'] = True
    games[gameid]['X'] = X
    games[gameid]['O'] = O

def move(gameid, move):
    game = games[gameid]
    if game['isPlaying']:
        if game['turn'] == 'X':
            #drawBoard(game['board'])
            move = getPlayerMove(game['board'])
            makeMove(game['board'], 'X', move)

            if isWinner(game['board'], 'X'):
                #drawBoard(game['board'])
                print('X won the game')
                game['isPlaying'] = False
            else:
                if isBoardFull(game['board']):
                    #drawBoard(game['board'])
                    print('Tie')
                    break
                else:
                    turn = 'O'

        else:
            #drawBoard(game['board'])
            move = getPlayerMove(game['board'])
            makeMove(game['board'], 'O', move)

            if isWinner(game['board'], 'O'):
                #drawBoard(game['board'])
                print('O won the game')
                game['isPlaying'] = False
            else:
                if isBoardFull(game['board']):
                    #drawBoard(game['board'])
                    print('Tie')
                    break
                else:
                    turn = 'X'
    else:
        print("Tried to move in a game that finished")
        # return -1 for invalid, 0 for good in progress, 1 for win, 2 for win

def serve_forever(host, port):
    # create, bind. listen
    lstsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # re-use the port
    lstsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # put listening socket into non-blocking mode
    lstsock.setblocking(0)

    lstsock.bind((host, port))
    lstsock.listen(BACKLOG)

    print ('Listening on port %d ...' % port)

    # read, write, exception lists with sockets to poll
    rlist, wlist, elist = [lstsock], [], []

    while True:
        # block in select
        readables, writables, exceptions = select.select(rlist, wlist, elist)

        for sock in readables:
            if sock is lstsock: # new client connection, we can accept now
                try:
                    conn, client_address = lstsock.accept()
                except IOError as e:
                    code, msg = e.args
                    if code == errno.EINTR:
                        continue
                    else:
                        raise
                # add the new connection to the 'read' list to poll
                # in the next loop cycle
                rlist.append(conn)
            else:
                # read a line that tells us how many bytes to write
                bytes = sock.recv(1024)
                print(bytes)
                if not bytes: # connection closed by client
                    sock.close()
                    rlist.remove(sock)
                else:
                    print(sock)
                    print ('Got request to send %s bytes. '
                           'Sending them all to...' % bytes)
                    # send them all
                    # XXX: this is cheating, we should use 'select' and wlist
                    # to determine whether socket is ready to be written to
                    data = os.urandom(int(bytes))
                    sock.sendall(data)


def main():
    parser = optparse.OptionParser()
    parser.add_option(
        '-i', '--host', dest='host', default='0.0.0.0',
        help='Hostname or IP address. Default is 0.0.0.0'
        )

    parser.add_option(
        '-p', '--port', dest='port', type='int', default=2000,
        help='Port. Default is 2000')

    options, args = parser.parse_args()

    serve_forever(options.host, options.port)

if __name__ == '__main__':
    main()