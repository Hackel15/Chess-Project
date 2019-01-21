from tkinter import *
import threading
import time

class ChessPiece():
      def __init__(self, chessType, player):
            self.pieces = ['Pawn','Rook','Knight','Bishop','Queen','King','Empty']
            self.type = self.validateType(chessType)
            self.player = self.validatePlayer(player)

      def validateType(self, userInput):
            for t in self.pieces:
                  if ( userInput == t ):
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

      def __str__(self):
            return "Chess Type: " + self.type + ", Position: " + str(self.position) + ", Player: " + str(self.player)
             
class Queen(ChessPiece):
      def __init__(self, player):
            super().__init__("Queen", player)

      def __str__(self):
            return super().__str__()            

class King(ChessPiece):
      def __init__(self, player):
            super().__init__("King", player)

      def __str__(self):
            return super().__str__()

class Rook(ChessPiece):
      def __init__(self, player):
            super().__init__("Rook", player)

      def __str__(self):
            return super().__str__()

class Pawn(ChessPiece):
      def __init__(self, player):
            super().__init__("Pawn", player)

      def __str__(self):
            return super().__str__()

class Knight(ChessPiece):
      def __init__(self, player):
            super().__init__("Knight", player)

      def __str__(self):
            return super().__str__()

class Bishop(ChessPiece):
      def __init__(self, player):
            super().__init__("Bishop", player)

      def __str__(self):
            return super().__str__()
            
class ChessBoard():
      def __init__(self):
            self.Board = []
            self.SZ = 8
            #initialize empty squares
            for row in range(self.SZ):
                  rowB = []
                  for col in range(self.SZ):
                        rowB.append(ChessPiece("Empty", -1))
                  self.Board.append(rowB)
            #initialize chess pieces
            self.Board[0][0] = Rook(2)
            self.Board[0][7] = Rook(2)
            self.Board[0][1] = Knight(2)
            self.Board[0][6] = Knight(2)
            self.Board[0][2] = Bishop(2)
            self.Board[0][5] = Bishop(2)
            self.Board[0][3] = Queen(2)
            self.Board[0][4] = King(2)

            self.Board[7][0] = Rook(1)
            self.Board[7][7] = Rook(1)
            self.Board[7][1] = Knight(1)
            self.Board[7][6] = Knight(1)
            self.Board[7][2] = Bishop(1)
            self.Board[7][5] = Bishop(1)
            self.Board[7][3] = Queen(1)
            self.Board[7][4] = King(1)
            
            for col in range(self.SZ):
                  self.Board[1][col] = Pawn(2)
                  self.Board[6][col] = Pawn(1)

      def getChessBoard(self):
            return self.Board
            
class MoveEngine():
      def __init__(self):
            self.castling = {}
            self.castling[0] = False
            self.castling[4] = False
            self.castling[7] = False
            self.castling[56] = False
            self.castling[60] = False
            self.castling[63] = False  
            self.upORdownMoves = [1,0, 0,-1, -1,0, 0,1]
            self.diagnolMoves = [1,1, 1,-1, -1,1, -1,-1]
            self.knightMoves = [ 1,2,  1,-2,  2,1,  2,-1, -1,2,  -2,1, -2,-1,  -1,-2 ]
            self.SZ = 8
            newBoard = ChessBoard()
            self.gameBoard = newBoard.getChessBoard()
            self.king_1 = 60
            self.king_2 = 4
            self.leftRook_1 = 56
            self.rightRook_1 = 63
            self.leftRook_2 = 0
            self.rightRook_2 = 7

      def printBoard(self):
            for row in range(self.SZ):
                  for col in range(self.SZ):
                        if (self.gameBoard[row][col].getType() != "Empty"):
                              print (self.gameBoard[row][col].getType()[0], end="  ")
                        else:
                              print (end="   ")
                  print('\n')

      def setBoard(self, newBoard):
            self.gameBoard = newBoard

      def getBoard(self):
            return self.gameBoard

      def getPiece(self, row, col):
            return self.gameBoard[row][col]

      def getPieceType(self, row, col):
            if (self.gameBoard[row][col].getType() != "Empty"):
                  return self.gameBoard[row][col].getType()
            
      def isEnemy(self, row, col, currentPlayer):
            if (self.gameBoard[row][col].getPlayer() != currentPlayer and self.isEmptySquare(row,col) == False):
                  return True
            return False

      def isValidSquare(self, row, col):
            if ((row < self.SZ) and (col < self.SZ) and (row >= 0) and (col >= 0)):
                  return True
            return False

      def isEmptySquare(self, row, col):
            if (self.gameBoard[row][col].getType()== "Empty"):
                  return True
            return False

      def isValidChoice(self, choice, moves):
            for cell in moves:
                  if (choice == cell):
                        return True
            return False

      def rowCol_toInt(self, row, col):
            return (self.SZ * row) + col

      def int_toRowCol(self, square):
            x = int(square / self.SZ)
            y = square % self.SZ
            return (x, y)

      def makeMove(self, cFrom, cTo):
            x, y = self.int_toRowCol(cFrom)
            c, d = self.int_toRowCol(cTo)
            print("{}{}{}{}{}{}{}{}{}".format("From: (", x, ',', y, ") To: (", c, ',', d, ")"))
            temp = self.gameBoard[x][y]
            self.gameBoard[c][d] = temp
            self.gameBoard[x][y] = ChessPiece("Empty", -1)
                              
      def executeMove(self, cellFrom, cellTo):
            cellFrom = self.rowCol_toInt(cellFrom[0], cellFrom[1])
            cellTo = self.rowCol_toInt(cellTo[0], cellTo[1])
            
            if (cellFrom == self.king_2 and self.castling[self.king_2] == False):
                  if (cellTo == 2 and self.castling[self.leftRook_2] == False):
                        self.makeMove(cellFrom, cellTo)
                        self.makeMove(self.leftRook_2, 3)
                        return
                  elif (cellTo == 6 and self.castling[self.rightRook_2] == False):
                        self.makeMove(cellFrom, cellTo)
                        self.makeMove(self.rightRook_2, 5)
                        return
            elif (cellFrom == self.king_1 and self.castling[self.king_1] == False):
                  if (cellTo == 58 and self.castling[self.leftRook_1] == False):
                        self.makeMove(cellFrom, cellTo)
                        self.makeMove(self.leftRook_1, 59)
                        return
                  elif (cellTo == 62 and self.castling[self.rightRook_1] == False):
                        self.makeMove(cellFrom, cellTo)
                        self.makeMove(self.rightRook_1, 61)
                        return
      
            #Castling limits
            for cell in self.castling:
                  if (cell == cellFrom):
                        self.castling[cell] = True
            self.makeMove(cellFrom, cellTo)
            return
      
      def move(self, row, col):
            possibleMoves = []
            if (isinstance(self.getPiece(row, col),Pawn)):
                  possibleMoves = self.getPawnMoves(row, col)
            elif (isinstance(self.getPiece(row, col),Knight)):
                  possibleMoves = self.getKnightMoves(row, col)
            elif (isinstance(self.getPiece(row, col),Bishop)):
                  possibleMoves = self.getGeneralMoves(row, col, self.diagnolMoves)
            elif (isinstance(self.getPiece(row, col),Rook)):
                  possibleMoves = self.getGeneralMoves(row, col, self.upORdownMoves)
            elif (isinstance(self.getPiece(row, col),Queen)):
                  possibleMoves = self.getGeneralMoves(row, col, self.diagnolMoves)
                  possibleMoves += self.getGeneralMoves(row, col, self.upORdownMoves)
            elif (isinstance(self.getPiece(row, col),King)):
                  possibleMoves = self.getKingMoves(row, col)
                  possibleMoves += self.checkCastlingMoves(row, col) #Check for castling
            return possibleMoves

      #FOR VUNERABLE MOVES
      def getGeneralMoves(self, row, col, move, player, vunerable_option, selected):
            possibleMoves = []
            for i in range(0, len(moves), 2):
                  CAUTION = 10
                  WARN = True
                  flag = True
                  tRow = row
                  tCol = col
                  while (CAUTION and WARN):
                        tRow += move[i]
                        tCol += move[i+1]
                        if (IsValidMove(tRow, tCol)):
                              if (IsEnemy(tRow, tCol, player)):
                                    possibleMoves.append((tRow, tCol))
                                    flag = False
                                    if (RowCol_toInt(tRow, tCol) != selected):
                                          WARN = False                              
                              elif (IsEmptySquare(tRow, tCol)):
                                    possibleMoves.append((tRow, tCol))
                              elif (RowCol_ToInt(tRow, tCol) == vunerable_option and flag):
                                    possibleMoves.append((tRow, tCol))
                              else:
                                    break
                  CAUTION -= 1
            return possibleMoves

      #FOR GENERAL MOVES           
      def getGeneralMoves(self, row, col, move):
            player = self.getPiece(row,col).getPlayer()
            possibleMoves = []
            for i in range(0, len(move), 2):
                  CAUTION = 10
                  flag = True
                  tRow = row
                  tCol = col
                  while ((CAUTION) and (flag)):
                        tRow += move[i]
                        tCol += move[i + 1]
                        if (self.isValidSquare(tRow, tCol)):
                              if (self.isEnemy(tRow, tCol, player)):
                                    possibleMoves.append((tRow, tCol))
                                    flag = False
                                    break
                              elif (self.isEmptySquare(tRow, tCol)):
                                    possibleMoves.append((tRow, tCol))
                              else:
                                    flag = False
                                    break
                        CAUTION -= 1
            return possibleMoves

      #FOR GENERAL MOVES
      def getKnightMoves(self, row, col):
            player = self.getPiece(row,col).getPlayer()
            possibleMoves = []
            for i in range(0, len(self.knightMoves), 2):
                  x = row + self.knightMoves[i]
                  y = col + self.knightMoves[i+1]
                  if (self.isValidSquare(x, y)):
                        if (self.isEnemy(x, y, player) or self.isEmptySquare(x, y)):
                              possibleMoves.append((x, y))
            return possibleMoves

      #FOR GENERAL MOVES
      def getKingMoves(self, row, col):
            player = self.getPiece(row,col).getPlayer()
            possibleMoves = []
            for i in range(0, len(self.upORdownMoves), 2):
                  x = row + self.upORdownMoves[i]
                  y = col + self.upORdownMoves[i+1]
                  if(self.isValidSquare(x,y)):
                        if(self.isEnemy(x,y,player) or self.isEmptySquare(x,y)):
                              possibleMoves.append((x,y))

            for i in range(0, len(self.diagnolMoves), 2):
                  x = row + self.diagnolMoves[i]
                  y = col + self.diagnolMoves[i+1]
                  if(self.isValidSquare(x,y)):
                        if(self.isEnemy(x,y,player) or self.isEmptySquare(x,y)):
                              possibleMoves.append((x,y))
                              
            return possibleMoves

      #FOR GENERAL MOVES
      def checkCastlingMoves(self, row, col):
            flag = True
            possibleMoves = []
            player = self.getPiece(row,col).getPlayer()
            square = self.rowCol_toInt(row, col)
            #Check Player 2
            if ( square == self.king_2 and player == 2):
                  if (self.castling[square] == False and (self.castling[self.leftRook_2] == False or self.castling[self.rightRook_2] == False)):
                        if (self.castling[self.leftRook_2]==False):
                              for i in range(self.leftRook_2+1, square):
                                    x, y = self.int_toRowCol(i)
                                    if(self.isEmptySquare(x, y) == False):
                                          flag = False
                              if (flag):
                                    possibleMoves.append(self.int_toRowCol(square - 2))
                        flag = True
                        if (self.castling[self.rightRook_2]==False):
                              for i in range(square+1, self.rightRook_2):
                                    x, y = self.int_toRowCol(i)
                                    if(self.isEmptySquare(x, y) == False):
                                          flag = False
                              if (flag):
                                    possibleMoves.append(self.int_toRowCol(square + 2))
            #Check Player 1
            elif ( square == self.king_1 and player == 1):
                  if (self.castling[square] == False and (self.castling[self.leftRook_2] == False) or (self.castling[self.rightRook_1] == False)):
                        if (self.castling[self.leftRook_1]==False):
                              for i in range(self.leftRook_1+1, square):
                                    x, y = self.int_toRowCol(i)
                                    if(self.isEmptySquare(x, y) == False):
                                          flag = False
                                          print("No Castling Available")
                              if (flag):
                                    possibleMoves.append(self.int_toRowCol(square - 2))
                        flag = True
                        if (self.castling[self.rightRook_1]==False):
                              for i in range(square+1, self.rightRook_1):
                                    x, y = self.int_toRowCol(i)
                                    if(self.isEmptySquare(x, y)==False):
                                          flag = False
                                          print("No Castling Available")
                              if (flag):
                                    possibleMoves.append(self.int_toRowCol(square + 2))
            print("CASTLING: " + str(possibleMoves) + " SQUARE: " + str(square))
            return possibleMoves
                                    

      #FOR GENERAL MOVES
      def getPawnMoves(self, row, col):
            player = self.getPiece(row,col).getPlayer()
            print("PLAYER: " + str(player))
            possibleMoves = []
            #CHECK PLAYER 1
            if (player == 1):
      		#check starting move
                  if (self.isValidSquare(row-2, col)):
                        if (row == 6 and self.getPiece(row-2,col).getType() == "Empty"):
                              possibleMoves.append((row - 2, col))
		#check square ahead
                  if (self.isValidSquare(row-1, col)):
                        if (self.getPiece(row-1,col).getType() == "Empty"):
                              possibleMoves.append((row - 1, col))
		#check diagnols for enemies
                  if (self.isValidSquare(row - 1, col - 1)):
                        if (self.isEnemy(row - 1, col - 1, player)):
                              possibleMoves.append((row - 1, col - 1))
		#check diagnols for enemies
                  if (self.isValidSquare(row - 1, col + 1)):
                        if (self.isEnemy(row - 1, col + 1, player)):
                              possibleMoves.append((row - 1, col + 1))

            #CHECK PLAYER 2
            elif (player == 2):
      		#check starting move
                  if (self.isValidSquare(row + 2, col)):
                        if (row == 1 and self.getPiece(row+2,col).getType() == "Empty"):
                              possibleMoves.append((row + 2, col))
		#check square ahead
                  if (self.isValidSquare(row  + 1, col)):
                        if (self.getPiece(row+1,col).getType() == "Empty"):
                              possibleMoves.append((row + 1, col))
		#check diagnols for enemies
                  if (self.isValidSquare(row + 1, col - 1)):
                        if (self.isEnemy(row + 1, col - 1, player)):
                              possibleMoves.append((row + 1, col - 1))
		#check diagnols for enemies
                  if (self.isValidSquare(row + 1, col + 1)):
                        if (self.isEnemy(row + 1, col + 1, player)):
                              possibleMoves.append((row + 1, col + 1))
            return possibleMoves

class App():
      def __init__(self):
            self.master = Tk()
            self.gameEngine = MoveEngine()
            self.canvas = Canvas(self.master, width=500, height=500, borderwidth=0, highlightthickness=0)
            self.canvas.pack(side="top", fill="both", expand="true")
            self.canvas.bind("<Configure>", self.redraw)
            self.status = Label(self.master, anchor="w")
            self.status.pack(side="bottom", fill="x")
            self.button = Button(self.master, text="Quit", command=lambda : self.close_window(self.master))
            self.button.pack()
            self.rows = 8
            self.columns = 8
            self.currentPlayer = 1
            self.selectedSquare = -1, -1
            self.cellChoice = -1, -1
            self.myPossibleMoves = []
            self.myVunerabilities = []
            self.tiles = {}
            self.t = threading.Thread(target=self.process)
            self.t.start()
            self.master.mainloop()

      def close_window(self, root):
            print('DESTROY')
            root.destroy()
            self.t.join()
      
      def rowCol_toInt(self, row, col):
            return (8 * row) + col

      def process(self):
            while(1):
                  print( "Process Data" )
                  r = input("Row:")
                  c = input("Col:")
                  if (self.gameEngine.isValidSquare(int(r), int(c))):
                        self.clicked(int(r), int(c))
      
      def redraw(self, event=None):
            self.canvas.delete("rect")
            cellwidth = int(self.canvas.winfo_width()/self.columns)
            cellheight = int(self.canvas.winfo_height()/self.columns)
            for column in range(self.columns):
                  for row in range(self.rows):
                        x1 = column*cellwidth
                        y1 = row * cellheight
                        x2 = x1 + cellwidth
                        y2 = y1 + cellheight
                        tile = self.canvas.create_rectangle(x1,y1,x2,y2, fill="white", tags="rect")
                        self.tiles[row,column] = tile
                        if (self.gameEngine.getPiece(row, column).getPlayer() == 1):
                              self.canvas.create_text((x1+x2)/2, (y1+y2)/2, anchor=CENTER, text=self.gameEngine.getPieceType(row,column), fill='blue')
                        else:
                              self.canvas.create_text((x1+x2)/2, (y1+y2)/2, anchor=CENTER, text=self.gameEngine.getPieceType(row,column), fill='red')
                  
            
      def clicked(self, row, column):
            tile = self.tiles[row,column]
            self.cellChoice = row, column
            if ((self.gameEngine.getPiece(row, column).getPlayer() == self.currentPlayer) and (self.selectedSquare[0] < 0) and (self.selectedSquare[1] < 0)):
                  self.selectedSquare = (row, column)
                  self.myPossibleMoves = self.gameEngine.move(row, column)
                  print("Possible Moves: " + str(self.myPossibleMoves))
                  if (len(self.myPossibleMoves) >= 1):
                        for r, c in self.myPossibleMoves:
                              self.canvas.itemconfigure(self.tiles[r, c], fill="green")
                  self.canvas.itemconfigure(tile, fill="green")
            elif (self.selectedSquare[0] >= 0 and self.selectedSquare[1] >= 0):
                  if (self.cellChoice == self.selectedSquare):
                        self.cellChoice = -1,-1
                        self.selectedSquare = -1,-1
                        self.myPossibleMoves = []
                  elif (self.gameEngine.isValidChoice(self.cellChoice, self.myPossibleMoves)):
                        self.gameEngine.executeMove(self.selectedSquare, self.cellChoice)
                        if (self.currentPlayer == 1): self.currentPlayer = 2
                        else: self.currentPlayer = 1
                        self.cellChoice = -1,-1
                        self.selectedSquare = -1,-1
                        self.myPossibleMoves = []
                        self.gameEngine.printBoard()
                  else:
                        pass
                  self.redraw()
            self.status.configure(text="You clicked on %s/%s | Player %d" % (row, column, self.currentPlayer))

if __name__ == "__main__":
    app = App()
            
