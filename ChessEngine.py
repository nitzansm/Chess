import numpy as np


class GameState():
    def __init__(self):
        # 1 => black 2 => white
        # 1 => R 2 => N 3 => B 4 => Q 5 => K 6 => p
        # 0 => empty spot
        self.board = np.array([[11, 12, 13, 14, 15, 13, 12, 11],
                                [16, 16, 16, 16, 16, 16, 16, 16],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [26, 26, 26, 26, 26, 26, 26, 26],
                                [21, 22, 23, 24, 25, 23, 22, 21]], np.int32)
        self.pieceToNum = {"R": 1, "N": 2, "B": 3, "Q": 4, "K": 5, "p": 6}
        self.colorToNum = {"-": 0, "b": 1, "w": 2}

        self.moveFunctions = {5: self.getKingMoves, 4: self.getQueenMoves, 1: self.getRookMoves,
                              3: self.getBishopMoves, 2: self.getKnightMoves, 6: self.getPawnMoves}
        self.whiteToMove = True
        self.moveLog = []# saving all the past moves
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = ()
        self.enpassantPossibleLog = [self.enpassantPossible]
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]

    def makeMove(self, move, realMove=False):
        self.board[move.startRow][move.startCol] = 0
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        if move.pieceMoved == self.colorToNum["w"]*10+self.pieceToNum["K"]:
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == self.colorToNum["b"]*10+self.pieceToNum["K"]:
            self.blackKingLocation = (move.endRow, move.endCol)

        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = (move.pieceMoved//10)*10+self.pieceToNum["Q"]

        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = 0

        if move.pieceMoved % 10 == self.pieceToNum["p"] and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.endCol)
        else:
            self.enpassantPossible = ()

        if move.isCastleMove:
            if realMove:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = 0
                else:
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                    self.board[move.endRow][move.endCol - 2] = 0

        self.enpassantPossibleLog.append(self.enpassantPossible)

        self.updateCastleRights(move, realMove)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                 self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

    def undoMove(self, realMove=False):
        if len(self.moveLog) > 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == self.colorToNum["w"]*10+self.pieceToNum["K"]:
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == self.colorToNum["b"]*10+self.pieceToNum["K"]:
                self.blackKingLocation = (move.startRow, move.startCol)

            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = 0
                self.board[move.startRow][move.endCol] = move.pieceCaptured

            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]

            if move.isCastleMove and realMove:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = 0
                else:
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = 0

            self.castleRightsLog.pop()

            self.currentCastlingRight = self.castleRightsLog[-1]

            self.checkMate = False
            self.staleMate = False

    def updateCastleRights(self, move, realMove=False):
        if realMove:
            if move.pieceMoved == self.colorToNum["w"]*10+self.pieceToNum["K"]:
                self.currentCastlingRight.wks = False
                self.currentCastlingRight.wqs = False
            elif move.pieceMoved == self.colorToNum["b"]*10+self.pieceToNum["K"]:
                self.currentCastlingRight.bks = False
                self.currentCastlingRight.bqs = False
            elif move.pieceMoved == self.colorToNum["w"]*10+self.pieceToNum["R"]:
                if move.startRow == 7:
                    if move.startCol == 0:
                        self.currentCastlingRight.wqs = False
                    elif move.startCol == 7:
                        self.currentCastlingRight.wks = False
            elif move.pieceMoved == self.colorToNum["b"]*10+self.pieceToNum["R"]:
                if move.startRow == 0:
                    if move.startCol == 0:
                        self.currentCastlingRight.bqs = False
                    elif move.startCol == 7:
                        self.currentCastlingRight.bks = False

            if move.pieceCaptured == self.colorToNum["w"]*10+self.pieceToNum["R"]:
                if move.endRow == 7:
                    if move.endCol == 0:
                        self.currentCastlingRight.wqs = False
                    elif move.endCol == 7:
                        self.currentCastlingRight.wks = False
            elif move.pieceCaptured == self.colorToNum["b"]*10+self.pieceToNum["R"]:
                if move.endRow == 0:
                    if move.endCol == 0:
                        self.currentCastlingRight.bqs = False
                    elif move.endCol == 7:
                        self.currentCastlingRight.bks = False

    def geValidMoves(self):
        tempEnpassant = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                        self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False
        self.enpassantPossible = tempEnpassant
        self.currentCastlingRight = tempCastleRights
        return moves

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for m in oppMoves:
            if m.endRow == r and m.endCol == c:
                return True
        return False

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c]//10
                if (turn == self.colorToNum["w"] and self.whiteToMove) or (turn == self.colorToNum["b"] and not self.whiteToMove):
                    piece = self.board[r][c] % 10
                    self.moveFunctions[piece](r, c, moves)
        return moves

    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:
            if self.board[r - 1][c] == 0:
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == 0:
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0 and self.board[r - 1][c - 1]//10 == self.colorToNum['b']:
                moves.append(Move((r, c), (r - 1, c - 1), self.board))
            elif (r - 1, c - 1) == self.enpassantPossible:
                moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove=True))
            if c + 1 < len(self.board[r]) and self.board[r - 1][c + 1]//10 == self.colorToNum['b']:
                moves.append(Move((r, c), (r - 1, c + 1), self.board))
            elif (r - 1, c + 1) == self.enpassantPossible:
                moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove=True))
        else:
            if self.board[r + 1][c] == 0:
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == 0:
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0 and self.board[r + 1][c - 1]//10 == self.colorToNum['w']:
                moves.append(Move((r, c), (r + 1, c - 1), self.board))
            elif (r + 1, c - 1) == self.enpassantPossible:
                moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove=True))
            if c + 1 < len(self.board[r]) and self.board[r + 1][c + 1]//10 == self.colorToNum['w']:
                moves.append(Move((r, c), (r + 1, c + 1), self.board))
            elif (r + 1, c + 1) == self.enpassantPossible:
                moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove=True))

    def getRookMoves(self, r, c, moves):
        mycolor = self.board[r][c]//10
        i = r - 1
        while i >= 0:  # going up
            if mycolor == self.board[i][c]//10:
                break
            elif self.board[i][c] != 0:
                moves.append(Move((r, c), (i, c), self.board))
                break
            moves.append(Move((r, c), (i, c), self.board))
            i -= 1
        i = r + 1
        while i < len(self.board):  # going down
            if mycolor == self.board[i][c]//10:
                break
            elif self.board[i][c]//10 != 0:
                moves.append(Move((r, c), (i, c), self.board))
                break
            moves.append(Move((r, c), (i, c), self.board))
            i += 1
        j = c + 1
        while j < len(self.board[r]):  # going right
            if mycolor == self.board[r][j]//10:
                break
            elif self.board[r][j]//10 != 0:
                moves.append(Move((r, c), (r, j), self.board))
                break
            moves.append(Move((r, c), (r, j), self.board))
            j += 1
        j = c - 1
        while j >= 0:
            if mycolor == self.board[r][j]//10:
                break
            elif self.board[r][j]//10 != 0:
                moves.append(Move((r, c), (r, j), self.board))
                break
            moves.append(Move((r, c), (r, j), self.board))
            j -= 1

    def getBishopMoves(self, r, c, moves):
        dire = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = self.colorToNum["b"] if self.whiteToMove else self.colorToNum["w"]
        for d in dire:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == 0:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece//10 == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = self.colorToNum["w"] if self.whiteToMove else self.colorToNum["b"]
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece//10 != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getQueenMoves(self, r, c, moves):
        self.getBishopMoves(r, c, moves)
        self.getRookMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = self.colorToNum["w"] if self.whiteToMove else self.colorToNum["b"]
        for i in kingMoves:
            endRow = r + i[0]
            endCol = c + i[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece//10 != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return
        if (self.whiteToMove and self.currentCastlingRight.wks) or (
                not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingSideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (
                not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueenSideCastleMoves(r, c, moves)

    def getKingSideCastleMoves(self, r, c, moves):
        if self.board[r][c + 1] == 0 and self.board[r][c + 2] == 0:
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    def getQueenSideCastleMoves(self, r, c, moves):
        if self.board[r][c - 1] == 0 and self.board[r][c - 2] == "--" and self.board[r][c - 3] == 0:
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():
    numToColor = {0: "-", 1: "b", 2: "w"}
    colorToNum = {v: k for k, v in numToColor.items()}
    numToPiece = {1: "R", 2: "N", 3: "B", 4: "Q", 5: "K", 6: "p"}
    pieceToNum = {v: k for k, v in numToPiece.items()}
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = (self.pieceMoved == self.colorToNum["w"]*10+self.pieceToNum["p"] and self.endRow == 0) or (
                self.pieceMoved == self.colorToNum["b"]*10+self.pieceToNum["p"] and self.endRow == 7)
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = self.colorToNum["w"]*10+self.pieceToNum["p"] if self.pieceMoved == self.colorToNum["b"]*10+self.pieceToNum["p"] else self.colorToNum["b"]*10+self.pieceToNum["p"]
        self.isCastleMove = isCastleMove
        self.isCapture = self.pieceCaptured != 0
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def __eq__(self, other):
        if isinstance(other, Move):
            return other.moveID == self.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol) + " "

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    def __str__(self):
        if self.isCastleMove:
            return "O-O" if self.endCol == 6 else "O-O-O"
        endSquare = self.getRankFile(self.endRow, self.endCol)

        if self.pieceMoved%10 == self.pieceToNum["p"]:
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "X" + endSquare
            else:
                return endSquare

        moveString = self.numToPiece[self.pieceMoved % 10]
        if self.isCapture:
            moveString += "X"
        return moveString + endSquare
