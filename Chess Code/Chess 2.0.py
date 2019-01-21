# Electronic Chess Board
from tkinter import *
import RPi.GPIO as GPIO
import threading
from multiprocessing import Process
import time

ROW = 8
COL = 8
SIZE = 8

castling = {0: False, 4: False, 7: False, 56: False, 60: False, 63: False}
king_1 = 60
king_2 = 4
leftRook_1 = 56
rightRook_1 = 63
leftRook_2 = 0
rightRook_2 = 7
castle_chance = False


def rowCol_toInt(row, col):
    return (SIZE * row) + col


def int_toRowCol(square):
    x = int(square / SIZE)
    y = square % SIZE
    return x, y


def printBoard():
    for row in range(SIZE):
        for col in range(SIZE):
            if global_board[row][col].getType() != "Empty":
                print(global_board[row][col].getType()[0], end="  ")
            else:
                print(end="   ")
        print('\n')


def getPiece(row, col):
    return global_board[row][col]


def getPieceType(row, col):
    if (global_board[row][col].getType() != "Empty"):
        return global_board[row][col].getType()

def isEnemy(row, col, currentPlayer):
    if (global_board[row][col].getPlayer() != currentPlayer and isEmptySquare(row, col) == False):
        return True
    return False


def isValidSquare(row, col):
    if ((row < SIZE) and (col < SIZE) and (row >= 0) and (col >= 0)):
        return True
    return False


def isEmptySquare(row, col):
    if (global_board[row][col].getType() == "Empty"):
        return True
    return False


def isValidChoice(choice, moves):
    for cell in moves:
        if (choice == cell):
            return True
    return False


class ChessPiece:
    def __init__(self, chessType, player):
        self.pieces = ['Pawn', 'Rook', 'Knight', 'Bishop', 'Queen', 'King', 'Empty']
        self.type = self.validateType(chessType)
        self.player = self.validatePlayer(player)
        self.upORdownMoves = [1, 0, 0, -1, -1, 0, 0, 1]  # POSSIBLE WAYS TO MOVE
        self.diagnolMoves = [1, 1, 1, -1, -1, 1, -1, -1]  # POSSIBLE WAYS TO MOVE

    def validateType(self, userInput):
        for t in self.pieces:
            if userInput == t:
                return userInput
        return "Empty"

    def validatePlayer(self, play):
        if (play):
            return play
        else:
            return -1

    def setType(self, chessType):
        self.type = chessType

    def getType(self):
        return self.type

    def setPlayer(self, play):
        self.player = play

    def getPlayer(self):
        return self.player

    # FOR GENERAL MOVES
    def getGeneralMoves(self, row, col, move):
        player = getPiece(row, col).getPlayer()
        possibleMoves = []
        for i in range(0, len(move), 2):
            CAUTION = 10
            flag = True
            tRow = row
            tCol = col
            while ((CAUTION) and (flag)):
                tRow += move[i]
                tCol += move[i + 1]
                if (isValidSquare(tRow, tCol)):
                    if (isEnemy(tRow, tCol, player)):
                        possibleMoves.append((tRow, tCol))
                        flag = False
                        break
                    elif isEmptySquare(tRow, tCol):
                        possibleMoves.append((tRow, tCol))
                    else:
                        flag = False
                        break
                CAUTION -= 1
        return possibleMoves

    #GET GENERAL ATTACKS
    def get_general_attacks(self, row, col, moves, vulnerable_option, selected):
        possibleMoves = []
        for i in range(0, len(moves), 2):
            CAUTION = 10
            WARN = True
            flag = True
            tRow = row
            tCol = col
            while (CAUTION and WARN):
                tRow += moves[i]
                tCol += moves[i + 1]
                if isValidSquare(tRow, tCol):
                    chess_piece = global_board[tRow][tCol]
                    if isEnemy(tRow, tCol, chess_piece.getPlayer()):
                        possibleMoves.append((tRow, tCol))
                        flag = False
                        if (tRow, tCol) != selected:
                            WARN = False
                    elif (isEmptySquare(tRow, tCol)):
                        possibleMoves.append((tRow, tCol))
                    elif (tRow, tCol) == vulnerable_option and flag:
                        possibleMoves.append((tRow, tCol))
                    elif (tRow, tCol) == selected and flag:
                        possibleMoves.append((tRow, tCol))
                    else:
                        break
                CAUTION -= 1
        return possibleMoves

    def __str__(self):
        return "Chess Type: " + self.type + " Player: " + str(self.player)


class Queen(ChessPiece):
    def __init__(self, player):
        super().__init__("Queen", player)

    def __str__(self):
        return super().__str__()

    def get_move(self, row, col):
        return self.getGeneralMoves(row, col, self.upORdownMoves) + \
               self.getGeneralMoves(row, col, self.diagnolMoves)

    def get_attacks(self, row, col, attacker, vulnerable_option, selected):
        return self.get_general_attacks(row, col, self.upORdownMoves, vulnerable_option, selected) + \
               self.get_general_attacks(row, col, self.diagnolMoves, vulnerable_option, selected)


class King(ChessPiece):
    def __init__(self, player):
        super().__init__("King", player)

    def __str__(self):
        return super().__str__()

    # FOR KING MOVES
    def get_move(self, row, col):
        return self.king_move(row, col) + self.castle_move(row, col)

    def king_move(self, row, col):
        player = getPiece(row, col).getPlayer()
        possibleMoves = []
        for i in range(0, len(self.upORdownMoves), 2):
            x = row + self.upORdownMoves[i]
            y = col + self.upORdownMoves[i + 1]
            if (isValidSquare(x, y)):
                if (isEnemy(x, y, player) or isEmptySquare(x, y)):
                    possibleMoves.append((x, y))

        for i in range(0, len(self.diagnolMoves), 2):
            x = row + self.diagnolMoves[i]
            y = col + self.diagnolMoves[i + 1]
            if (isValidSquare(x, y)):
                if (isEnemy(x, y, player) or isEmptySquare(x, y)):
                    possibleMoves.append((x, y))

        return possibleMoves

    def get_attacks(self, row, col, attacker, vulnerable_option, selected):
        player = getPiece(row, col).getPlayer()
        possibleMoves = []
        for i in range(0, len(self.upORdownMoves), 2):
            x = row + self.upORdownMoves[i]
            y = col + self.upORdownMoves[i + 1]
            if isValidSquare(x, y):
                square = rowCol_toInt(x, y)
                if isEnemy(x, y, player) or (isEmptySquare(x, y) and square == vulnerable_option):
                    possibleMoves.append((x, y))

        for i in range(0, len(self.diagnolMoves), 2):
            x = row + self.diagnolMoves[i]
            y = col + self.diagnolMoves[i + 1]
            if isValidSquare(x, y):
                square = rowCol_toInt(x, y)
                if isEnemy(x, y, player) or (isEmptySquare(x, y) and square == vulnerable_option):
                    possibleMoves.append((x, y))

        return possibleMoves

    # CHECK FOR CASTLING MOVES
    def castle_move(self, row, col):
        flag = True
        possibleMoves = []
        player = getPiece(row, col).getPlayer()
        square = rowCol_toInt(row, col)
        # Check Player 2
        if (square == king_2 and player == 2):
            if (castling[square] == False and (
                            castling[leftRook_2] == False or castling[rightRook_2] == False)):
                if (castling[leftRook_2] == False):
                    for i in range(leftRook_2 + 1, square):
                        x, y = int_toRowCol(i)
                        if (isEmptySquare(x, y) == False):
                            flag = False
                    if (flag):
                        possibleMoves.append(int_toRowCol(square - 2))
                flag = True
                if (castling[rightRook_2] == False):
                    for i in range(square + 1, rightRook_2):
                        x, y = int_toRowCol(i)
                        if (isEmptySquare(x, y) == False):
                            flag = False
                    if (flag):
                        possibleMoves.append(int_toRowCol(square + 2))
        # Check Player 1
        elif (square == king_1 and player == 1):
            if (castling[square] == False and (castling[leftRook_2] == False) or (
                        castling[rightRook_1] == False)):
                if (castling[leftRook_1] == False):
                    for i in range(leftRook_1 + 1, square):
                        x, y = int_toRowCol(i)
                        if (isEmptySquare(x, y) == False):
                            flag = False
                            print("No Castling Available")
                    if (flag):
                        possibleMoves.append(int_toRowCol(square - 2))
                flag = True
                if (castling[rightRook_1] == False):
                    for i in range(square + 1, rightRook_1):
                        x, y = int_toRowCol(i)
                        if (isEmptySquare(x, y) == False):
                            flag = False
                            print("No Castling Available")
                    if (flag):
                        possibleMoves.append(int_toRowCol(square + 2))
        print("CASTLING: " + str(possibleMoves) + " SQUARE: " + str(square))
        return possibleMoves


class Rook(ChessPiece):
    def __init__(self, player):
        super().__init__("Rook", player)

    def __str__(self):
        return super().__str__()

    def get_move(self, row, col):
        return self.getGeneralMoves(row, col, self.upORdownMoves)

    def get_attacks(self, row, col, attacker, vulnerable_option, selected):
        return self.get_general_attacks(row, col, self.upORdownMoves, vulnerable_option, selected)

class Pawn(ChessPiece):
    def __init__(self, player):
        super().__init__("Pawn", player)

    def __str__(self):
        return super().__str__()

    # FOR PAWN MOVES
    def get_move(self, row, col):
        player = getPiece(row, col).getPlayer()
        print("PLAYER: " + str(player))
        possibleMoves = []
        # CHECK PLAYER 1
        if (player == 1):
            # check square ahead
            if (isValidSquare(row - 1, col)):
                if (getPiece(row - 1, col).getType() == "Empty"):
                    possibleMoves.append((row - 1, col))
                    # check starting move
                    if (row == 6 and isValidSquare(row - 2, col)):
                        if (getPiece(row - 2, col).getType() == "Empty"):
                            possibleMoves.append((row - 2, col))
                            # check diagnols for enemies
            if (isValidSquare(row - 1, col - 1)):
                if (isEnemy(row - 1, col - 1, player)):
                    possibleMoves.append((row - 1, col - 1))
                    # check diagnols for enemies
            if (isValidSquare(row - 1, col + 1)):
                if (isEnemy(row - 1, col + 1, player)):
                    possibleMoves.append((row - 1, col + 1))

        # CHECK PLAYER 2
        elif (player == 2):
            # check square ahead
            if isValidSquare(row + 1, col):
                if (getPiece(row + 1, col).getType() == "Empty"):
                    possibleMoves.append((row + 1, col))
                    # check starting move
                    if (row == 1 and isValidSquare(row + 2, col)):
                        if (getPiece(row + 2, col).getType() == "Empty"):
                            possibleMoves.append((row + 2, col))
                            # check diagnols for enemies
            if (isValidSquare(row + 1, col - 1)):
                if (isEnemy(row + 1, col - 1, player)):
                    possibleMoves.append((row + 1, col - 1))
                    # check diagnols for enemies
            if (isValidSquare(row + 1, col + 1)):
                if (isEnemy(row + 1, col + 1, player)):
                    possibleMoves.append((row + 1, col + 1))
        return possibleMoves

    def get_attacks(self, row, col, attacker, vulnerable_option, selected):
        move = []
        #Attacker is player 1
        if attacker == 1:
            if isValidSquare(row - 1, col - 1):
                if vulnerable_option == rowCol_toInt(row - 1, col - 1):
                    move.append((row - 1, col -1))
                if selected == rowCol_toInt(row - 1, col - 1):
                    move.append((row - 1, col - 1))
            if isValidSquare(row - 1, col + 1):
                if vulnerable_option == rowCol_toInt(row - 1, col + 1):
                    move.append((row - 1, col + 1))
                if selected == rowCol_toInt(row - 1, col + 1):
                    move.append((row - 1, col + 1))

        #Attacker is player 2
        elif attacker == 2:
            if isValidSquare(row + 1, col + 1):
                if vulnerable_option == rowCol_toInt(row + 1, col + 1):
                    move.append((row + 1, col + 1))
                if selected == rowCol_toInt(row + 1, col + 1):
                    move.append((row + 1, col + 1))
            if isValidSquare(row + 1, col - 1):
                if vulnerable_option == rowCol_toInt(row + 1, col - 1):
                    move.append((row + 1, col - 1))
                if selected == rowCol_toInt(row + 1, col -1):
                    move.append((row + 1, col - 1))

        return move


class Knight(ChessPiece):
    def __init__(self, player):
        super().__init__("Knight", player)
        self.knightMoves = [1, 2, 1, -2, 2, 1, 2, -1, -1, 2, -2, 1, -2, -1, -1, -2]  # POSSIBLE WAYS TO MOVE

    def __str__(self):
        return super().__str__()

    # FOR KNIGHT MOVES
    def get_move(self, row, col):
        player = getPiece(row, col).getPlayer()
        possible_moves = []
        for i in range(0, len(self.knightMoves), 2):
            x = row + self.knightMoves[i]
            y = col + self.knightMoves[i + 1]
            if isValidSquare(x, y):
                if isEnemy(x, y, player) or isEmptySquare(x, y):
                    possible_moves.append((x, y))
        return possible_moves

    def get_attacks(self, row, col, attacker, vulnerable_choice, selected):
        #print(vulnerable_choice)
        player = getPiece(row, col).getPlayer()
        possible_moves = []
        for i in range(0, len(self.knightMoves), 2):
            x = row + self.knightMoves[i]
            y = col + self.knightMoves[i + 1]
            if isValidSquare(x, y):
                square = rowCol_toInt(x, y)
                if isEnemy(x, y, player) or (isEmptySquare(x, y) and square == vulnerable_choice): #made change......
                    possible_moves.append((x, y))
        return possible_moves


class Bishop(ChessPiece):
    def __init__(self, player):
        super().__init__("Bishop", player)

    def __str__(self):
        return super().__str__()

    def get_move(self, row, col):
        return self.getGeneralMoves(row, col, self.diagnolMoves)

    def get_attacks(self, row, col, attacker, vulnerable_option, selected):
        return self.get_general_attacks(row, col, self.diagnolMoves, vulnerable_option, selected)


def make_board():
    gameBoard = []
    # initialize empty squares
    for row in range(SIZE):
        rowB = []
        for col in range(SIZE):
            rowB.append(ChessPiece("Empty", -1))
        gameBoard.append(rowB)
    # initialize chess pieces
    gameBoard[0][0] = Rook(2)
    gameBoard[0][7] = Rook(2)
    gameBoard[0][1] = Knight(2)
    gameBoard[0][6] = Knight(2)
    gameBoard[0][2] = Bishop(2)
    gameBoard[0][5] = Bishop(2)
    gameBoard[0][3] = Queen(2)
    gameBoard[0][4] = King(2)

    gameBoard[7][0] = Rook(1)
    gameBoard[7][7] = Rook(1)
    gameBoard[7][1] = Knight(1)
    gameBoard[7][6] = Knight(1)
    gameBoard[7][2] = Bishop(1)
    gameBoard[7][5] = Bishop(1)
    gameBoard[7][3] = Queen(1)
    gameBoard[7][4] = King(1)

    for col in range(SIZE):
        gameBoard[1][col] = Pawn(2)
        gameBoard[6][col] = Pawn(1)

    castling = {0: False, 4: False, 7: False, 56: False, 60: False, 63: False}
    king_1 = 60
    king_2 = 4
    leftRook_1 = 56
    rightRook_1 = 63
    leftRook_2 = 0
    rightRook_2 = 7
    castle_chance = False

    return gameBoard


class MoveEngine:
    def __init__(self):
        self.SZ = 8

    def makeMove(self, cFrom, cTo):
        x, y = int_toRowCol(cFrom)
        c, d = int_toRowCol(cTo)
        print("{}{}{}{}{}{}{}{}{}".format("From: (", x, ',', y, ") To: (", c, ',', d, ")"))
        temp = global_board[x][y]
        global_board[c][d] = temp
        global_board[x][y] = ChessPiece("Empty", -1)

        return global_board

    def executeMove(self, cellFrom, cellTo):
        cellFrom = rowCol_toInt(cellFrom[0], cellFrom[1])
        cellTo = rowCol_toInt(cellTo[0], cellTo[1])

        if (cellFrom == king_2 and castling[king_2] == False):
            if (cellTo == 2 and castling[leftRook_2] == False):
                self.makeMove(cellFrom, cellTo)
                self.makeMove(leftRook_2, 3)
                return
            elif (cellTo == 6 and castling[rightRook_2] == False):
                self.makeMove(cellFrom, cellTo)
                self.makeMove(rightRook_2, 5)
                return
        elif (cellFrom == king_1 and castling[king_1] == False):
            if (cellTo == 58 and castling[leftRook_1] == False):
                self.makeMove(cellFrom, cellTo)
                self.makeMove(leftRook_1, 59)
                return
            elif (cellTo == 62 and castling[rightRook_1] == False):
                self.makeMove(cellFrom, cellTo)
                self.makeMove(rightRook_1, 61)
                return
        # Castling limits
        for cell in castling:
            if (cell == cellFrom):
                castling[cell] = True
        self.makeMove(cellFrom, cellTo)
        return

    # CALCULATES ALL POSSIBLE MOVES
    def move(self, row, col):
        piece = global_board[row][col]
        return piece.get_move(row, col)

    # FOR VUNERABLE MOVES
    def get_vulnerable(self, vulnerable_square, selected, attacker):
        moves = []
        the_moves = []
        s = selected
        v = vulnerable_square
        selected = rowCol_toInt(selected[0], selected[1])
        vulnerable_square = rowCol_toInt(vulnerable_square[0], vulnerable_square[1])
        for row in range(0, SIZE):
            for col in range(0, SIZE):
                chess_piece = getPiece(row, col)
                if chess_piece.getPlayer() == attacker and isEmptySquare(row, col) == False:
                    moves.append(chess_piece.get_attacks(row, col, attacker, vulnerable_square, selected))
                    #print(chess_piece)
                    #print(moves)
                for m in moves:
                    for p in m:
                        if p == v or p == s:
                            the_moves.append(p)
                moves.clear()
        return the_moves


    #PICK UP FROM HERE

global_board = make_board()


def reset_board():
    global global_board
    global_board = make_board()


class App:
    def __init__(self, master):
        self.root = master
        self.game_engine = MoveEngine()
        reset_board()

        # self.data = -1
        # VARIABLES FOR GAME PLAY
        self.currentPlayer = 1
        self.selectedSquare = -1, -1
        self.cellChoice = -1, -1

        self.myPossibleMoves = []
        # self.myPossibleMoves = []
        self.myVulnerabilities = []

        # GAME STATUS
        self.gameStatus = -1
        self.tiles = {}

        # GUI OBJECTS
        self.canvas = Canvas(self.root, width=600, height=600, borderwidth=0, highlightthickness=0)
        self.canvas.pack(side="top", fill="both", expand="true")
        self.canvas.bind("<Configure>", self.redraw)
        self.status = Label(self.root, anchor="w")
        self.status.pack(side="bottom", fill="x")
        # self.btn_text = StringVar()
        # self.btn_text.set("Pause")
        self.button1 = Button(self.root, text="Quit", command=lambda: self.close_window(self.root))
        # self.button2 = Button(self.master, text="Start", command=lambda: self.start())
        # self.button3 = Button(self.master, textvariable=self.btn_text, command=lambda: self.pause())
        self.button1.pack(side="bottom")
        # self.button2.pack(side="bottom")
        # self.button3.pack(side="bottom")
        # self.move_handler = StatusChecker()
        self.root.mainloop()

    ##      def pause(self):
    ##            if (self.gameStatus == 1):
    ##                  self.gameStatus = 2
    ##                  self.btn_text.set("Resume")
    ##                  self.master.after_cancel(self.call)
    ##                  print('Pausing Game')
    ##
    ##            elif (self.gameStatus == 2):
    ##                  self.gameStatus = 1
    ##                  self.btn_text.set("Pause")
    ##                  self.call = self.master.after(1, self.callback)
    ##
    ##      def callback(self):
    ##            dataList = self.move_handler.getData()
    ##            if (dataList <= 0):
    ##                  print("No move found...")
    ##                  pass
    ##            elif (dataList > 0):
    ##                  print("Square " + str(dataList) + " chosen")
    ##
    ##            self.call = self.master.after(1, self.callback)
    ##
    ##      def start(self):
    ##            if (self.gameStatus == -1):
    ##                  self.gameStatus = 1
    ##                  self.move_handler.start()
    ##                  self.call = self.master.after_idle(self.callback)

    def close_window(self, master):
        print("Destroy")
        # del (self.move_handler)
        master.destroy()

    def getGameEngine(self):
        return self.game_engine

    def redraw(self, event=None):
        self.canvas.delete("rect")
        cellwidth = int(self.canvas.winfo_width() / COL)
        cellheight = int(self.canvas.winfo_height() / COL)
        for col in range(COL):
            for row in range(ROW):
                x1 = col * cellwidth
                y1 = row * cellheight
                x2 = x1 + cellwidth
                y2 = y1 + cellheight
                tile = self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", tags="rect")
                self.tiles[row, col] = tile
                if getPiece(row, col).getPlayer() == 1:
                    self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, anchor=CENTER,
                                            text=getPieceType(row, col), fill='blue')
                else:
                    self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, anchor=CENTER,
                                            text=getPieceType(row, col), fill='red')
                self.canvas.tag_bind(tile, "<Button-1>", lambda event=None, row=row, col=col: self.game(row, col))

    def game(self, row, column):
        if isValidSquare(row, column):
            print('Selected: ' + getPiece(row, column).getType())
            tile = self.tiles[row, column]
            self.cellChoice = row, column
            #Click for the first time (must click on player's chesspiece 
            if ((getPiece(row, column).getPlayer() == self.currentPlayer) and (
                        self.selectedSquare[0] < 0) and (self.selectedSquare[1] < 0)):
                self.selectedSquare = (row, column)
                self.myPossibleMoves = self.game_engine.move(row, column)
                print("Possible Moves: " + str(self.myPossibleMoves))
                if self.currentPlayer == 1:
                    attacker = 2
                else:
                    attacker = 1
                print("Searching for vulnerabilities!!")
                for move in self.myPossibleMoves:
                    position = self.game_engine.get_vulnerable(move, self.selectedSquare, attacker)
                    if len(position) > 0:
                        self.myVulnerabilities.append(position)
                    print(self.myVulnerabilities)
                #print(self.myVulnerabilities)
                print("FINISHED VUL")
                
                if len(self.myPossibleMoves) >= 1:
                    for r, c in self.myPossibleMoves:
                        self.canvas.itemconfigure(self.tiles[r, c], fill="green")
                self.canvas.itemconfigure(tile, fill="green")
                #print(self.myVulnerabilities)
                if len(self.myVulnerabilities) > 0:
                    for x in self.myVulnerabilities:
                        print(x)
                        for r, c in x:
                            self.canvas.itemconfigure(self.tiles[r, c], fill="yellow")
                print('sleep 1 second')
                time.sleep(1)
            #Deselect selected chesspiece
            elif (self.selectedSquare[0] >= 0 and self.selectedSquare[1] >= 0):
                if (self.cellChoice == self.selectedSquare):
                    if (len(self.myPossibleMoves) > 1):
                        for r, c in self.myPossibleMoves:
                            self.canvas.itemconfigure(self.tiles[r, c], fill="white")
                    self.canvas.itemconfigure(tile, fill="white")
                    if len(self.myVulnerabilities) > 0:
                        for x in self.myVulnerabilities:
                            for r, c in x:
                                self.canvas.itemconfigure(self.tiles[r, c], fill="yellow")
                    self.cellChoice = -1, -1
                    self.selectedSquare = -1, -1
                    self.myPossibleMoves = []
                    self.myVulnerabilities = []
                    self.redraw()
                    print('sleep 1 second')
                    time.sleep(1)
                elif isValidChoice(self.cellChoice, self.myPossibleMoves):
                    self.game_engine.executeMove(self.selectedSquare, self.cellChoice)
                    if (self.currentPlayer == 1):
                        self.currentPlayer = 2
                    else:
                        self.currentPlayer = 1
                    self.cellChoice = -1, -1
                    self.selectedSquare = -1, -1
                    self.myVulnerabilities = []
                    self.myPossibleMoves = []
                    printBoard()
                    self.redraw()
                else:
                    pass

            self.status.configure(text="you clicked on %s/%s | Player %d" % (row, column, self.currentPlayer))

class Led:
    def __init__(self):
        #Ground Control
        self.ground1 = 13
        self.ground2 = 6
        self.ground3 = 5
        #LED Color Control
        self.red = 18
        self.green = 23
        self.blue = 20
        #LED MUX Control
        self.led1 = 24
        self.led2 = 25
        self.led3 = 12

        #OUTPUT SETUP
        GPIO.setup(self.ground1, GPIO.OUT)
        GPIO.setup(self.ground2, GPIO.OUT)
        GPIO.setup(self.ground3, GPIO.OUT)
        GPIO.setup(self.red, GPIO.OUT)
        GPIO.setup(self.green, GPIO.OUT)
        GPIO.setup(self.blue, GPIO.OUT)
        GPIO.setup(self.led1, GPIO.OUT)
        GPIO.setup(self.led2, GPIO.OUT)
        GPIO.setup(self.led3, GPIO.OUT)

        GPIO.output(self.ground1, GPIO.LOW)
        GPIO.output(self.ground2, GPIO.LOW)
        GPIO.output(self.ground3, GPIO.LOW)
        GPIO.output(self.red, GPIO.LOW)
        GPIO.output(self.green, GPIO.LOW)
        GPIO.output(self.blue, GPIO.LOW)
        GPIO.output(self.led1, GPIO.LOW)
        GPIO.output(self.led2, GPIO.LOW)
        GPIO.output(self.led3, GPIO.LOW)

    def testBoard(self):
        for i in range(8):
            GPIO.output(self.led1, (GPIO.HIGH and (i & 1)))
            GPIO.output(self.led2, (GPIO.HIGH and (i & 10)))
            GPIO.output(self.led3, (GPIO.HIGH and (i & 100)))
            for j in range(8):
                GPIO.output(self.ground1, (GPIO.HIGH and (i & 1)))
                GPIO.output(self.ground2, (GPIO.HIGH and (i & 10)))
                GPIO.output(self.ground3, (GPIO.HIGH and (i & 100)))
                time.sleep(1)
        


# class StatusChecker(threading.Thread):
#     """
#     The thread that will check player moves
#     """
#
#     def __init__(self):
#         super().__init__()
#         self.pieces_lifted = 0
#         self.interface = Interface()
#
#     def run(self):
#         self.pieces_lifted = self.interface.search()
#         print('Successssss')
#
#     def getData(self):
#         data = self.pieces_lifted
#         self.pieces_lifted = 0
#         return data
#
#     def deleteData(self):
#         self.pieces_lifted.clear()


##class Interface:
##    def __init__(self):
##        self.output1 = 18 ##MUX OUTPUTS
##        self.output2 = 23
##        self.output3 = 24
##
##        self.input1 = 17  ##DIGITAL INPUTS
##        self.input2 = 27
##        self.input3 = 22
##        self.input4 = 5
##        self.input5 = 6
##        self.input6 = 13
##        self.input7 = 19
##        self.input8 = 26
##
##        self.input1Array = [0]*8 ##BOARD INPUT VALUES
##        self.input2Array = [0]*8
##        self.input3Array = [0]*8
##        self.input4Array = [0]*8
##        self.input5Array = [0]*8
##        self.input6Array = [0]*8
##        self.input7Array = [0]*8
##        self.input8Array = [0]*8
##
##        GPIO.setmode(GPIO.BCM)  ##GPIO SETUP
##        GPIO.setup(self.output1, GPIO.OUT)
##        GPIO.setup(self.output2, GPIO.OUT)
##        GPIO.setup(self.output3, GPIO.OUT)
##
##        GPIO.setup(self.input1, GPIO.IN)
##        GPIO.setup(self.input2, GPIO.IN)
##        GPIO.setup(self.input3, GPIO.IN)
##        GPIO.setup(self.input4, GPIO.IN)
##        GPIO.setup(self.input5, GPIO.IN)
##        GPIO.setup(self.input6, GPIO.IN)
##        GPIO.setup(self.input7, GPIO.IN)
##        GPIO.setup(self.input8, GPIO.IN)
##
##    def printMux(self):
##        self.updateMux()
##        allArrays = self.sortBoardArray()
##        for x in range(64):
##            if ( x % 8 == 0  and x != 0 ):
##                print('\n')
##            if ( allArrays[x] == 1 ):
##                  pass
##            else:
##                  print('%02d' % ((x)), end="  ")
##        print('\n'*4)
##        time.sleep(1)
##
##    def sortBoardArray(self):
##        allArrays = []
##        allArrays += (self.input1Array)
##        allArrays += (self.input2Array)
##        allArrays += (self.input3Array)
##        allArrays += (self.input4Array)
##        allArrays += (self.input5Array)
##        allArrays += (self.input6Array)
##        allArrays += (self.input7Array)
##        allArrays += (self.input8Array)
##        sortedArray = []
##        for x in range(0, 64, 16):
##            sortedArray += allArrays[x+0:x+4] + allArrays[x+8:x+12] + allArrays[x+4:x+8] + allArrays[x+12:x+16]
##        return sortedArray
##
##    def updateMux(self):
##        for i in range(8):
##            GPIO.output(self.output1, (GPIO.HIGH and (i & 1)))
##            GPIO.output(self.output2, (GPIO.HIGH and (i & 10)))
##            GPIO.output(self.output3, (GPIO.HIGH and (i & 100)))
##
##            self.input1Array[i] = GPIO.input(self.input1)
##            self.input2Array[i] = GPIO.input(self.input2)
##            self.input3Array[i] = GPIO.input(self.input3)
##            self.input4Array[i] = GPIO.input(self.input4)
##            self.input5Array[i] = GPIO.input(self.input5)
##            self.input6Array[i] = GPIO.input(self.input6)
##            self.input7Array[i] = GPIO.input(self.input7)
##            self.input8Array[i] = GPIO.input(self.input8)
##
##    def searchInputData(self):
##        lifted = []
##        dataArray = self.sortBoardArray()
##        for data in range(len(dataArray)):
##            if (dataArray[data] == 0):
##                return data
##        return -1
##
##    def search(self):
##        print('SEARCHING FOR SIGNAL')
##        flag = True
##        while(flag):
##            self.updateMux()
##            data = self.searchInputData()
##            if (data >= 0 and data < 64):
##                flag = False
##            print('no move in interface')
##        return data
##
##
##if __name__ == "__main__":
##    "master = Tk()"
##    "game = App(master)"
##    interface = Interface()
##    while True:
##          interface.printMux()
##
##GPIO.cleanup()

root = Tk()
game = App(root)


# Run Application -- Prompts chess window to open with initial options: Game selection--Player vs. AI, Player vs. Player--Learning, Beginner, Advanced
# Learning--Displays possible moves & vunerabilities of pieces #Beginner--Displays possible moves #Advanced--Play a standard game of chess$$


# Run a thread to always search for player pieces that move.  Okay.  Once a piece is found to be moved, then store the data (position) in a list). Okay.
# The data will be stored within a list and updated continuously in real time.  This thread runs and runs and runs -- because how else would we search for movement
# on the board.  Now.... We need to send this updated data or stream it into the game program and handle the lifted pieces as processed.
##Electronic Chess Board
