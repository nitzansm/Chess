import random

pieceScore = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "p": 1}
knightScore = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1, 1]
]

bishopScore = [
    [4, 3, 2, 1, 1, 2, 3, 4],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [4, 3, 2, 1, 1, 2, 3, 4]
]

queenScore = [
    [1, 1, 1, 3, 1, 1, 1, 1],
    [1, 2, 3, 3, 3, 1, 1, 1],
    [1, 4, 3, 3, 3, 4, 2, 1],
    [1, 2, 3, 3, 3, 2, 2, 1],
    [1, 2, 3, 3, 3, 2, 2, 1],
    [1, 4, 3, 3, 3, 4, 2, 1],
    [1, 1, 2, 3, 3, 1, 1, 1],
    [1, 1, 1, 3, 1, 1, 1, 1]
]

rookScore = [
    [4, 3, 4, 4, 4, 4, 3, 4],
    [4, 4, 4, 4, 4, 4, 4, 4],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [4, 4, 4, 4, 4, 4, 4, 4],
    [4, 3, 4, 4, 4, 4, 3, 4]
]

whitePawnScore = [[10, 10, 10, 10, 10, 10, 10, 10],
                  [8, 8, 8, 8, 8, 8, 8, 8],
                  [5, 6, 6, 7, 7, 6, 6, 5],
                  [2, 3, 3, 5, 5, 3, 3, 2],
                  [1, 2, 3, 4, 4, 3, 2, 1],
                  [1, 1, 2, 3, 3, 2, 1, 1],
                  [1, 1, 1, 0, 0, 1, 1, 1],
                  [0, 0, 0, 0, 0, 0, 0, 0]]

blackPawnScore = [[0, 0, 0, 0, 0, 0, 0, 0],
                  [1, 1, 1, 0, 0, 1, 1, 1],
                  [1, 1, 2, 3, 3, 2, 1, 1],
                  [1, 2, 3, 4, 4, 3, 2, 1],
                  [2, 3, 3, 5, 5, 3, 3, 2],
                  [5, 6, 6, 7, 7, 6, 6, 5],
                  [8, 8, 8, 8, 8, 8, 8, 8],
                  [10, 10, 10, 10, 10, 10, 10, 10]
                  ]
piecePositionScores = {"N": knightScore, "B": bishopScore, "Q": queenScore, "R": rookScore, "bp": blackPawnScore, "wp": whitePawnScore}

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3


def findRandomMove(validMoves):
    if len(validMoves) > 0:
        return validMoves[random.randint(0, len(validMoves) - 1)]


def findBestMove(gs, validMoves, returnQueue):
    global nextMove, count
    count = 0
    nextMove = None
    #random.shuffle(validMoves)
    # findMoveMinMax(gs, validMoves, DEPTH, gs.whiteToMove)
    # findMoveNegaMax(gs, validMoves, DEPTH, 1 if gs.whiteToMove else -1)
    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    returnQueue.put(nextMove)
    print(count)
    #return nextMove


def findMoveNegaMax(gs, validMoves, depth, turnMult):
    global nextMove
    if depth == 0:
        return turnMult * scoreBoard(gs)

    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.geValidMoves()
        score = -findMoveNegaMax(gs, nextMoves, depth - 1, -turnMult)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()

    return maxScore


def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMult):
    global nextMove, count
    count += 1
    if depth == 0:
        return turnMult * scoreBoard(gs)

    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.geValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMult)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
                print(move, score)
        gs.undoMove()
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore


def findMoveMinMax(gs, validMoves, depth, whiteToMove):  # recursive minMax
    global nextMove
    if depth == 0:
        return scoreBoard(gs)
    if whiteToMove:
        maxScore = - CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.geValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, False)
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
            score = findMoveMinMax(gs, nextMoves, depth - 1, True)
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
    board = gs.board
    for r in range(len(gs.board)):
        for c in range(len(gs.board[r])):
            if board[r][c] != "--":
                piecePositionScore = 0
                if board[r][c][1] != "K":
                    if board[r][c][1] != "p":
                        piecePositionScore = piecePositionScores[board[r][c][1]][r][c]
                    else:
                        piecePositionScore = piecePositionScores[board[r][c]][r][c]
                if board[r][c][0] == "w":
                    score += pieceScore[board[r][c][1]] + piecePositionScore * 0.1
                elif board[r][c][0] == "b":
                    score -= pieceScore[board[r][c][1]] + piecePositionScore * 0.1
    return score


def findBestMoveMinMax2(gs, validMoves):  # recursive version
    global nextMove
    nextMove = None
    findMoveMinMax(gs, validMoves, DEPTH, gs.whiteToMove)
    return nextMove


def findBestMoveMinMax1(gs, validMoves):  # minMax 2  moves loops version
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


def findBestMoveGreedy(gs, validMoves):  # greedy version
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
        gs.undoMove()
    return bestMove


def scoreMaterial(board):  # maybe add positioning score
    score = 0
    for row in board:
        for square in row:
            if square[0] == "w":
                score += pieceScore[square[1]]
            elif square[0] == "b":
                score -= pieceScore[square[1]]
    return score
