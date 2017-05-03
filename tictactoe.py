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

def newgame():
    theBoard = [' '] * 10
    player1, player2 = "X", "O"
    turn = "X"
    gameIsPlaying = True

    while gameIsPlaying:
        if turn == 'X':
            drawBoard(theBoard)
            move = getPlayerMove(theBoard)
            makeMove(theBoard, player1, move)

            if isWinner(theBoard, player1):
                drawBoard(theBoard)
                print('X won the game')
                gameIsPlaying = False
            else:
                if isBoardFull(theBoard):
                    drawBoard(theBoard)
                    print('Tie')
                    break
                else:
                    turn = 'O'

        else:
            drawBoard(theBoard)
            move = getPlayerMove(theBoard)
            makeMove(theBoard, player2, move)

            if isWinner(theBoard, player2):
                drawBoard(theBoard)
                print('O won the game')
                gameIsPlaying = False
            else:
                if isBoardFull(theBoard):
                    drawBoard(theBoard)
                    print('Tie')
                    break
                else:
                    turn = 'X'

def main():
    newgame()

if __name__ == '__main__':
    main()