import sys
import random
import time

# Niklas Fiekas, python-chess, acessed in December 2022
# https://github.com/niklasf/python-chess
import chess
import chess.gaviota
import chess.polyglot
import chess.pgn

pawn = 1
knight = 2.5
bishop = 2.5
rook = 4
queen = 6
cutoff = 1.2
maxtime = 8
maxdepth = 16
emergency = False

color = 1 if sys.argv[1] == "white" else 0
gametime = 0
turn = 1

class AntiBoard(chess.Board): 
    @property
    def legal_moves(self):
        return MyLegalMoveGenerator(self)

class MyLegalMoveGenerator(chess.LegalMoveGenerator):
    def __iter__(self):
        return self.board.generate_legal_captures() if any(self.board.generate_legal_captures()) \
            else self.board.generate_legal_moves()

board = AntiBoard()
if color:
    move = "f2f3"
    board.push_san(move)
    print(str(move))

def IsTablebase(board):
    whitepieces, blackpieces = 0, 0
    for i in range(64):
        piece = str(board.piece_at(i))
        whitepieces += piece.isupper()
        blackpieces += piece.islower()
    return (whitepieces == 1 and blackpieces <= 3) or (whitepieces <= 3 and blackpieces == 1)

def RandomMove(board):
    if IsTablebase(board):
        return Endgame(board)
    moves = list(board.legal_moves)
    move = moves[random.randint(0,len(moves)-1)]
    #board.push(moves[random.randint(0,len(moves)-1)])
    return(str(move))

tablebase = chess.gaviota.open_tablebase("tablebase")

def Eval(board, color, isendgame, opponents, pawn, knight, bishop, rook, queen):
    wpieces, bpieces, value, attacks, pawns = 0, 0, 0, 0, 0
    values = {'P' : pawn, 'N' : knight, 'B' : bishop, 'R' : rook, 'Q' : queen, 'K' : 0, 'NONE': 0}
    for i in range(64):
        piece = str(board.piece_at(i))
        wpieces += piece.isupper()
        bpieces += piece.islower()
        value += values[piece.upper()] * (1 if piece.isupper() else -1)
        attacks += len(board.attacks(i)) * (-1 if board.color_at(i) else 1)
        if piece.upper() == 'P':
            pawns += i // 8 + 1 + (0 if piece.isupper() else -9)
    istablebase = (wpieces == 1 and bpieces <= 3) or (wpieces <= 3 and bpieces == 1)
    if isendgame:
        return (istablebase, ((((12 - wpieces - bpieces) * (abs(value) >= 2) * 10 * \
            (opponents < [wpieces, bpieces][color] or [wpieces, bpieces][color] == 1) + \
            abs(value))) * (1 if value >= 0 else -1) + 0.01 * pawns) * (1 if color else -1))
    return (istablebase, value * (1 if color else -1))

def Endgame(board):
    copyboard = board.copy()
    while not copyboard.is_checkmate():
        moves = list(copyboard.legal_moves)
        n = abs(tablebase.probe_dtm(copyboard))
        for move in moves:
            copyboard.push(move)
            if (n == 1 and copyboard.is_checkmate()) or \
            (n != 1 and abs(tablebase.probe_dtm(copyboard)) == n - 1):
                return str(move)
            copyboard.pop()

tablesize = 2**16
transtable = {} # index: [hash, depth, value, flag, move]
game = {}

def God(board, color, transtable, drawval):
    if len(list(board.legal_moves)) == 1:
        return str(list(board.legal_moves)[0])

    nodes = [0]
    isendgame = len([piece for piece in [board.piece_at(i) for i in range(64)] if piece != None]) <= 12
    opponents = len([piece for piece in [board.piece_at(i) for i in range(64)]
    if [str.isupper, str.islower][color](str(piece))])

    def alphabeta(node, depth, alpha, beta, maximizingPlayer, first, count):
        nodes[0] += 1
        capture = any(node.generate_legal_captures())
        istablebase, eval = Eval(node, color, isendgame, opponents, pawn, knight, bishop, rook, queen)
        hash = chess.polyglot.zobrist_hash(node)
        if node.is_game_over():
            outcome = node.outcome().result()
            return drawval if "/" in outcome else (200 if outcome[0] == "1" else -200) * (1 if color else -1)
        if hash in game and not first:
            return drawval
        if istablebase:
            dtm = tablebase.probe_dtm(node)
            return drawval if dtm == 0 else dtm/abs(dtm)*200 * (1 if maximizingPlayer else -1)
        current = eval
        if depth == 0 or count >= maxdepth:
            return current
        if not first and time.time() - start > maxtime:
            return None
        moves = list(node.legal_moves)
        if hash % tablesize in transtable:
            entry = transtable[hash % tablesize]
            if entry[0] == hash:
                moves = [chess.Move.from_uci(entry[4])] + moves
            if entry[0] == hash and entry[1] >= depth:
                drawcheck = False
                if first:
                    fake = node.copy()
                    fake.push_san(entry[4])
                    drawcheck = hash in game
                    for move in list(fake.legal_moves):
                        child = fake.copy()
                        child.push(move)
                        childhash = chess.polyglot.zobrist_hash(child)
                        drawcheck = drawcheck or childhash in game
                if not drawcheck:
                    if entry[3] == 0:
                        return (entry[4], entry[2]) if first else entry[2]
                    if entry[3] == 1 and entry[2] >= beta:
                        return (entry[4], entry[2]) if first else entry[2]
                    if entry[3] == -1 and entry[2] <= alpha:
                        return (entry[4], entry[2]) if first else entry[2]

        if maximizingPlayer:
            if depth == 1 and current + 0.3 < alpha and (not capture):
                return current
            value = -300
            flag = -1
            best = moves[0]
            for move in moves:
                child = node.copy()
                child.push(move)
                capturenext = any(child.generate_legal_captures())
                if i >= 5 and depth > 2:
                    v = alphabeta(child, 2, alpha, beta, False, False, count + 1)
                    if v != None and v >= alpha:
                        v = alphabeta(child, depth - 1 + capturenext, alpha, beta, False, False, count + 1)
                else:
                    v = alphabeta(child, depth - 1 + capturenext, alpha, beta, False, False, count + 1)
                if v == None:
                    return (None, None) if first else None
                if v > value:
                    value = v
                    best = move
                if value >= beta:
                    flag = 1
                    break
                if value >= alpha:
                    flag = 0
                    alpha = value
            transtable[hash % tablesize] = [hash, depth, value, flag, str(best)]
            return (str(best), value) if first else value
        else:
            if depth == 1 and current - 0.3 > beta and (not capture):
                return current
            value = 300
            flag = 1
            for move in moves:
                child = node.copy()
                child.push(move)
                capturenext = any(child.generate_legal_captures())
                if i >= 5 and depth > 2:
                    v = alphabeta(child, 2, alpha, beta, True, False, count + 1)
                    if v!= None and v <= beta:
                        v = alphabeta(child, depth - 1 + capturenext, alpha, beta, True, False, count + 1)
                else:
                    v = alphabeta(child, depth - 1 + capturenext, alpha, beta, True, False, count + 1)
                if v == None:
                    return (None, None) if first else None
                if v < value:
                    value = v
                    best = move
                if value <= alpha:
                    flag = -1
                    break
                if value <= beta:
                    flag = 0
                    beta = value
            transtable[hash % tablesize] = [hash, depth, value, flag, str(best)]
            return value
    
    if IsTablebase(board):
        return Endgame(board)
    
    if emergency:
        return RandomMove(board)

    for i in range(1, 20):
        start = time.time()
        move, val = alphabeta(board, i, -250, 250, True, True, 0)
        if move != None:
            bestmove = move
            bestval = val
        end = time.time()
        #print("Depth %s: %s, value %s, %s nodes searched, %s seconds." % (i, bestmove, bestval, nodes[0], round(end-start,2)))
        if end - start > cutoff:
            return bestmove
    return bestmove

while not board.is_game_over():
    s = input()
    board.push_san(s)
    hash = chess.polyglot.zobrist_hash(board)
    game[hash] = 1

    if board.is_game_over():
        break

    t = time.time()
    move = God(board, color, transtable, -1.2)
    gametime += time.time() - t
    board.push_san(move)
    print(str(move))
    hash = chess.polyglot.zobrist_hash(board)
    game[hash] = 1

    if gametime > 150:
        cutoff = 0.3
        maxtime = 4
    if gametime > 170:
        emergency = True
    turn += 1

print('End')

quit()
