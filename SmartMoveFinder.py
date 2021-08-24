import random


pieceScore = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "p": 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2

def findRandomMove(validMoves):
    if len(validMoves) > 0:
        return validMoves[random.randint(0, len(validMoves)-1)]


def findMoveMinMax(gs, validMoves, depth, whiteToMove):#recursive minMax
    global nextMove
    if depth == 0:
        return scoreBoard(gs)
    if whiteToMove:
        maxScore = - CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.geValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth-1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return maxScore
    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.geValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth-1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return minScore

def scoreBoard(gs):
    if gs.checkMate:
        if gs.whiteToMove:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.staleMate:
        return STALEMATE
    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == "w":
                score += pieceScore[square[1]]
            elif square[0] == "b":
                score -= pieceScore[square[1]]
    return score


def findBestMoveMinMax(gs, validMoves):
    global nextMove
    nextMove = None
    findMoveMinMax(gs, validMoves, DEPTH, gs.whiteToMove)
    return nextMove


def findBestMove(gs, validMoves):#minMax 2  moves loops version
    turnMult = 1 if gs.whiteToMove else -1
    opMinMaxScore = CHECKMATE
    bestPlayerMove = None
    random.shuffle(validMoves)
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        opMoves = gs.geValidMoves()
        if gs.staleMate:
            opMaxScore = STALEMATE
        elif gs.checkMate:
            opMaxScore = CHECKMATE
        else:
            opMaxScore = -CHECKMATE
        for opMove in opMoves:
            gs.makeMove(opMove)
            gs.geValidMoves()
            if gs.checkMate:
                score = CHECKMATE
            elif gs.staleMate:
                score = STALEMATE
            else:
                score = -scoreMaterial(gs.board) * turnMult
            if score > opMaxScore:
                opMaxScore = score
            gs.undoMove()
        if opMinMaxScore > opMaxScore:
            opMinMaxScore = opMaxScore
            bestPlayerMove = playerMove
        gs.undoMove()
    return bestPlayerMove

def findBestMoveGreedy(gs, validMoves):#greedy version
    turnMult = 1 if gs.whiteToMove else -1
    maxScore = -CHECKMATE
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        if gs.checkMate:
            score = -CHECKMATE
        elif gs.staleMate:
            score = STALEMATE
        else:
            score = -scoreMaterial(gs.board) * turnMult
        if score > maxScore:
            maxScore = score
            bestMove = playerMove
        #gs.undoMove()
    return bestMove

def scoreMaterial(board):  #maybe add positioning score
    score = 0
    for row in board:
        for square in row:
            if square[0] == "w":
                score += pieceScore[square[1]]
            elif square[0] == "b":
                score -= pieceScore[square[1]]
    return score
