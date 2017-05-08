import errno
import select
import socket
import optparse

BACKLOG = 5

games = [None] * 100
users = {}


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


def checkValidMove(board, move):
    if move not in '1 2 3 4 5 6 7 8 9'.split() or not isSpaceFree(board, int(move)):
        move = -1
    return int(move)


def isBoardFull(board):
    for i in range(1, 10):
        if isSpaceFree(board, i):
            return False
    return True


def newgame(gameid, X, O):
    games[gameid] = {}
    games[gameid]['board'] = [' '] * 10
    games[gameid]['turn'] = 'X'
    games[gameid]['turnuid'] = X
    games[gameid]['isPlaying'] = True
    games[gameid]['X'] = X
    games[gameid]['O'] = O


def move(gameid, move):
    game = games[gameid]
    if game['isPlaying']:
        if game['turn'] == 'X':
            move = checkValidMove(game['board'], move)
            if move == -1:
                return -1
            makeMove(game['board'], 'X', move)
            if isWinner(game['board'], 'X'):
                game['isPlaying'] = False
                return 1
            else:
                if isBoardFull(game['board']):
                    return 3
                else:
                    game['turn'] = 'O'
                    game['turnuid'] = game['O']
                    return 0

        else:
            move = checkValidMove(game['board'], move)
            if move == -1:
                return -1
            makeMove(game['board'], 'O', move)
            if isWinner(game['board'], 'O'):
                game['isPlaying'] = False
                return 2
            else:
                if isBoardFull(game['board']):
                    return 3
                else:
                    game['turn'] = 'X'
                    game['turnuid'] = game['X']
                    return 0


def startServer(host, port):
    lstsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lstsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lstsock.setblocking(0)
    lstsock.bind((host, port))
    lstsock.listen(BACKLOG)
    print('Serving up some Tic-Tac-Toe on ' + str(host) + ':' + str(port) + '...')
    rlist, wlist, elist = [lstsock], [], []
    while True:
        readables, writables, exceptions = select.select(rlist, wlist, elist)
        for sock in readables:
            if sock is lstsock:
                try:
                    conn, client_address = lstsock.accept()
                except IOError as e:
                    code, msg = e.args
                    if code == errno.EINTR:
                        continue
                    else:
                        raise
                rlist.append(conn)
            else:
                bytes = sock.recv(1024).decode()
                if not bytes:
                    sock.close()
                    rlist.remove(sock)
                else:
                    info = bytes.split('#')
                    if info[0] == '100':
                        name = info[1]
                        if name not in users:
                            users[name] = 'availible'
                            sock.sendall(('101#' + name).encode())
                        else:
                            sock.sendall(('401#Username already taken').encode())
                    elif info[0] == '110':
                        del users[info[1]]
                        sock.close()
                        rlist.remove(sock)
                    elif info[0] == '130':
                        if info[2] == '1':
                            responce = ''
                            for user in users:
                                responce += user + ',' + users[user] + ';'
                            sock.sendall(('131#' + responce).encode())
                        elif info[2] == '2':
                            responce = ''
                            for i, game in enumerate(games):
                                if game is not None:
                                    responce += str(i) + ',' + game['X'] + ',' + game['O'] + ';'
                            sock.sendall(('132#' + responce).encode())
                    elif info[0] == '199':
                        found = False
                        for i, game in enumerate(games):
                            if game is not None:
                                if (game['O'] == info[1] or game['X'] == info[1]) and game['isPlaying']:
                                    found = True
                                    sock.sendall(('213#' + str(i) + '#' + ''.join(game['board']) + '#' + game['turnuid'] + '#' + game['X'] + '#' + game['O']).encode())
                                elif (game['O'] == info[1] or game['X'] == info[1]) and game['isPlaying'] is False:
                                    found = True
                                    if isWinner(game['board'], 'X'):
                                        sock.sendall(('214#' + info[1] + '#' + 'O Won!').encode())
                                    elif isWinner(game['board'], 'O'):
                                        sock.sendall(('214#' + info[1] + '#' + 'X Won!').encode())
                                    else:
                                        sock.sendall(('214#' + info[1] + '#' + 'Tie!').encode())
                                    games[i] = None
                        if not found:
                            sock.sendall(('198#').encode())
                    elif info[0] == '200':
                        if info[2] not in users:
                            sock.sendall(('408#' + info[1] + '#Invited player does not exist').encode())
                        elif users[info[2]] == 'busy':
                            sock.sendall(('408#' + info[1] + '#Invited player busy').encode())
                        else:
                            gid = -1
                            for i in range(0, len(games)):
                                if games[i] is None:
                                    gid = i
                                    break
                            if gid != -1:
                                newgame(gid, info[1], info[2])
                                game = games[gid]
                                users[info[1]] = 'busy'
                                users[info[2]] = 'busy'
                                sock.sendall(('201#' + info[1] + '#' + str(gid)).encode())
                                sock.sendall(('213#' + str(gid) + '#' + ''.join(game['board']) + '#' + game['turnuid'] + '#' + game['X'] + '#' + game['O']).encode())
                            else:
                                sock.sendall(('408#' + info[1] + '#Out of game slots').encode())
                    elif info[0] == '204':
                        game = games[int(info[2])]
                        users[game['X']] = 'availible'
                        users[game['O']] = 'availible'
                        del users[info[1]]
                        game['isPlaying'] = False
                        sock.sendall(("205#" + info[1] + '#' + info[2]).encode())
                        sock.close()
                        rlist.remove(sock)
                    elif info[0] == '210':
                        ret = move(int(info[2]), info[3])
                        if ret == 0 or ret == -1:
                            sock.sendall(("211#" + info[1] + '#' + info[3]).encode())
                        elif ret == 1:
                            game = games[int(info[2])]
                            users[game['X']] = 'availible'
                            users[game['O']] = 'availible'
                            game['isPlaying'] = False
                            sock.sendall(('214#' + info[2] + '#' + 'O Won!').encode())
                        elif ret == 2:
                            game = games[int(info[2])]
                            users[game['X']] = 'availible'
                            users[game['O']] = 'availible'
                            game['isPlaying'] = False
                            sock.sendall(('214#' + info[2] + '#' + 'X Won!').encode())
                        elif ret == 3:
                            game = games[int(info[2])]
                            users[game['X']] = 'availible'
                            users[game['O']] = 'availible'
                            game['isPlaying'] = False
                            sock.sendall(('214#' + info[2] + '#' + 'Tie!').encode())
                    elif info[0] == '212':
                        game = games[int(info[2])]
                        sock.sendall(('213#' + info[2] + '#' + ''.join(game['board']) + '#' + game['turnuid'] + '#' + game['X'] + '#' + game['O']).encode())

                    else:
                        sock.sendall(("Not supported rn").encode())


def main():
    parser = optparse.OptionParser()
    parser.add_option('-i', dest='host', default='localhost', help='Hostname or IP address. Default is localhost')
    parser.add_option('-p', dest='port', type='int', default=9206, help='Port. Default is 9206')
    options, args = parser.parse_args()
    startServer(options.host, options.port)


if __name__ == '__main__':
    main()
