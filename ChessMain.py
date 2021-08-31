import pygame as p
import ChessEngine
import SmartMoveFinder
from multiprocessing import Process, Queue

BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT//2
TURN_HEIGHT = BOARD_HEIGHT - MOVE_LOG_PANEL_HEIGHT
TURN_WIDTH = 250
NOTATION_WIDTH = 50
NOTATION_HEIGHT = 40
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}
pieceToNum = {"R": 1, "N": 2, "B": 3, "Q": 4, "K": 5, "p": 6}
colorToNum = {"-": 0, "b": 1, "w": 2}


def loadImages():
    pieces = ["wp", "wR", "wN", "wB", "wK", "wQ", "bp", "bR", "bN", "bB", "bK", "bQ"]
    for piece in pieces:
        pieceName = colorToNum[piece[0]]*10 + pieceToNum[piece[1]]
        IMAGES[pieceName] = p.transform.scale(p.image.load("images/" + str(pieceName) + ".png"),
                                          (SQ_SIZE, SQ_SIZE))


def main():
    p.init()
    moveLogFont = p.font.SysFont("Arial", 15, False, False)
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH + NOTATION_WIDTH, BOARD_HEIGHT+NOTATION_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.geValidMoves()
    drawNotation(screen)
    animate = True
    moveMade = False
    loadImages()
    running = True
    sqSelected = ()
    playerClicks = []
    gameOver = False
    playerOne = True
    playerTwo = True
    AIThinking = False
    moveFinderProcess = None
    moveUndone = False
    flip = False
    while running:
        drawTurn(screen, gs.whiteToMove, playerOne, playerTwo)
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    animate, moveMade, sqSelected, playerClicks = playerTurn(animate, gs, humanTurn, moveMade,
                                                                             playerClicks, sqSelected, validMoves, flip)

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gameOver = False
                    gs.undoMove(realMove=True)
                    animate = False
                    moveMade = True
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
                if e.key == p.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.geValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
                if e.key == p.K_f:
                    flip = not flip
                if e.key == p.K_1:
                    playerOne = not playerOne
                if e.key == p.K_2:
                    playerTwo = not playerTwo

        if not gameOver and not humanTurn and not moveUndone:
            if not AIThinking:
                returnQueue = Queue()
            AIThinking, animate, moveFinderProcess, moveMade = AITurn(AIThinking, animate, gs, moveFinderProcess,
                                                                      moveMade, returnQueue, validMoves, flip)

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock, flip)
            validMoves = gs.geValidMoves()
            moveUndone = False
            animate = False
        drawGameState(screen, gs, validMoves, sqSelected, moveLogFont, flip)

        if gs.checkMate or gs.staleMate:
            gameOver = True
            text = "StaleMate" if gs.staleMate else (("Black " if gs.whiteToMove else "White ")+"wins by checkmate")
            drawEndGameText(screen, text)

        if len(gs.moveLog) > 0:
            highlightLastMove(screen, gs.moveLog[-1], flip)
            moveMade = False
        clock.tick(MAX_FPS)
        p.display.flip()


def AITurn(AIThinking, animate, gs, moveFinderProcess, moveMade, returnQueue, validMoves, flip):
    if not AIThinking:
        AIThinking = True

        moveFinderProcess = Process(target=SmartMoveFinder.findBestMove, args=(gs, validMoves, returnQueue))
        moveFinderProcess.start()
    if not moveFinderProcess.is_alive() and AIThinking:
        AIMove = returnQueue.get()
        if AIMove is None:
            AIMove = SmartMoveFinder.findRandomMove(validMoves)
        if AIMove is not None:
            gs.makeMove(AIMove, realMove=True)
            moveMade = True
            animate = True
        AIThinking = False
    return AIThinking, animate, moveFinderProcess, moveMade


def playerTurn(animate, gs, humanTurn, moveMade, playerClicks, sqSelected, validMoves, flip):
    location = p.mouse.get_pos()
    col = location[0] // SQ_SIZE
    row = location[1] // SQ_SIZE
    row = 7 - row if flip else row
    if sqSelected == (row, col) or col > 7 or row > 7 or row < 0 or col < 0:
        sqSelected = ()
        playerClicks = []
    else:
        #sqSelected = (row, col) if not flip else (7-row, col)
        sqSelected = (row, col)
        playerClicks.append(sqSelected)
    if len(playerClicks) == 2 and humanTurn:
        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
        """
        if flip:
            r, c = playerClicks[0]
            playerClicks[0] = (7 - r, c)
            r, c = playerClicks[1]
            playerClicks[1] = (7 - r, c)
        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
        """
        for i in range(len(validMoves)):
            if move == validMoves[i]:
                gs.makeMove(validMoves[i], realMove=True)
                animate = True
                moveMade = True
                sqSelected = ()
                playerClicks = []
        if not moveMade:
            playerClicks = [sqSelected]
    return animate, moveMade, sqSelected, playerClicks


def highlightSquares(screen, gs, validMoves, sqSelected, flip):
    if sqSelected != ():
        r, c = sqSelected
        con = (colorToNum["w"] if gs.whiteToMove else colorToNum["b"])
        if gs.board[r][c]//10 == con:
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(150)
            s.fill(p.Color("cyan"))
            row = 7 - r if flip else r
            screen.blit(s, (c * SQ_SIZE, row * SQ_SIZE))
            s.set_alpha(150)
            s.fill(p.Color("green"))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    row = (7-move.endRow) if flip else move.endRow
                    screen.blit(s, (move.endCol * SQ_SIZE, row * SQ_SIZE))


def highlightLastMove(screen, move, flip):
    r = move.endRow
    c = move.endCol
    s = p.Surface((SQ_SIZE, SQ_SIZE))
    s.set_alpha(150)
    s.fill(p.Color("brown"))
    if flip:
        r = 7 - r
    screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
    if move.isPawnPromotion:
        piece = (move.pieceMoved - pieceToNum["p"]) + pieceToNum["Q"]
        screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
    else:
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont, flip):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected, flip)
    drawPieces(screen, gs.board, flip)
    drawMoveLog(screen, gs, moveLogFont)


def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board, flip):

    if not flip:
        for r in range(DIMENSION):
            for c in range(DIMENSION):
                piece = board[r][c]
                if piece != 0:
                    screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
    else:
        for r in range(DIMENSION-1, -1, -1):
            for c in range(DIMENSION):
                piece = board[r][c]
                if piece != 0:
                    screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, (7-r) * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(BOARD_WIDTH+NOTATION_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT+NOTATION_HEIGHT).move(0, TURN_HEIGHT)
    p.draw.rect(screen, p.Color("grey"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    if len(moveLog) > 0:
        mod = len(moveLog) % 49 if len(moveLog) % 49 != 0 else 1
    else:
        mod = 0
    rng = range(len(moveLog) - mod, len(moveLog), 2)#take only the last 48 moves(the window can take only 48 moves)
    for i in rng:
        moveString = str(i//2 + 1)+". "+str(moveLog[i])
        moveString += (" "+str(moveLog[i+1])+" ")if i+1 < len(moveLog) else " "
        moveTexts.append(moveString)
    padding = 5
    textY = padding
    movesPerRow = 3
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i+j < len(moveTexts):
                text += moveTexts[i+j]
            else:
                break
        textObject = font.render(text, True, p.Color("black"))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)

        textY += textObject.get_height()


def drawNotation(screen):
    col = {0: "A", 1: "B", 2: "C", 3: "D", 4: "E", 5: "F", 6: "G", 7: "H"}
    font = p.font.SysFont("Arial", 32, True, False)
    for i in range(DIMENSION):
        text = col[i]
        textObject = font.render(text, 0, p.Color("black"))
        textLocation = p.Rect(i * SQ_SIZE, 8 * SQ_SIZE, SQ_SIZE, SQ_SIZE).move(SQ_SIZE//2.5, 0)
        screen.blit(textObject, textLocation)
    for i in range(DIMENSION):
        text = str(8-i)
        textObject = font.render(text, 0, p.Color("black"))
        textLocation = p.Rect(8 * SQ_SIZE, i * SQ_SIZE, SQ_SIZE, SQ_SIZE).move(SQ_SIZE//2.5, SQ_SIZE//4)
        screen.blit(textObject, textLocation)
    p.draw.rect(screen, "black", p.Rect(8 * SQ_SIZE, 8 * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawTurn(screen, whiteToMove, playerOne, playerTwo):
    text = "White" if whiteToMove else "Black"
    text += "'s turn to move"
    backGroundColor = p.Color("black") if whiteToMove else p.Color("white")
    turnRect = p.Rect(BOARD_WIDTH+NOTATION_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, backGroundColor, turnRect)
    font = p.font.SysFont("Helvetica", 20, True, False)
    color = p.Color("black") if not whiteToMove else p.Color("white")

    textObject = font.render(text, 0, color)
    textLocation = p.Rect((NOTATION_WIDTH+BOARD_WIDTH), 0, SQ_SIZE, SQ_SIZE).move(60, 100)
    screen.blit(textObject, textLocation)
    human = "a human "
    AI = "an AI "
    text = "White is being played by " + (human if playerOne else AI)
    font = p.font.SysFont("Helvetica", 18, True, False)
    textObject = font.render(text, 0, color)
    textLocation = p.Rect((NOTATION_WIDTH + BOARD_WIDTH), 0, SQ_SIZE, SQ_SIZE).move(15, 150)
    screen.blit(textObject, textLocation)
    text = "Black is being played by " + (human if playerTwo else AI)
    font = p.font.SysFont("Helvetica", 18, True, False)
    textObject = font.render(text, 0, color)
    textLocation = p.Rect((NOTATION_WIDTH + BOARD_WIDTH), 0, SQ_SIZE, SQ_SIZE).move(15, 180)
    screen.blit(textObject, textLocation)


def animateMove(move, screen, board, clock, flip):
    global colors
    startRow = 7 - move.startRow if flip else move.startRow
    endRow = 7 - move.endRow if flip else move.endRow
    dR = endRow - startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
        drawBoard(screen)
        drawPieces(screen, board, flip)
        color = colors[(move.endCol + endRow) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        if move.pieceCaptured != 0:
            if move.isEnpassantMove:
                endSquare = p.Rect(move.endCol * SQ_SIZE, startRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                screen.blit(IMAGES[move.pieceCaptured], endSquare)
            else:
                screen.blit(IMAGES[move.pieceCaptured], endSquare)
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def drawEndGameText(screen, text):
    font = p.font.SysFont("Arial", 32, True, False)
    textObject = font.render(text, 0, p.Color("black"))

    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObject.get_width() / 2,
                                                                BOARD_HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("orange"))
    screen.blit(textObject, textLocation.move(2, 2))


if __name__ == "__main__":
    main()
