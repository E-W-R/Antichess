import sys
import chess
import chess.gaviota
import chess.polyglot
import chess.pgn
import random
import math
import time
import statistics

#color = 1 if sys.argv[1] == "white" else 0

class AntiBoard(chess.Board): 
    @property
    def legal_moves(self):
        return MyLegalMoveGenerator(self)

class MyLegalMoveGenerator(chess.LegalMoveGenerator):
    def __iter__(self):
        return self.board.generate_legal_captures() if any(self.board.generate_legal_captures()) \
            else self.board.generate_legal_moves()

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

def Eval(board, color, isendgame, pawn, knight, bishop, rook, queen):
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
        return (istablebase, ((12 - wpieces - bpieces) * (value >= 2) * \
            (1 if value > 0 else -1) + 0.1 * value + 0.001 * pawns) * (1 if color else -1))
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

tablesize = 2**17
transtable = {} # index: [hash, depth, value, flag, move]
game = {}

def God(board, color, transtable, drawval):
    if len(list(board.legal_moves)) == 1:
        return str(list(board.legal_moves)[0])

    nodes = [0]
    isendgame = len([piece for piece in [board.piece_at(i) for i in range(64)] if piece != None]) <= 12
    def alphabeta(node, depth, alpha, beta, maximizingPlayer, first, count):
        nodes[0] += 1
        capture = any(node.generate_legal_captures())
        istablebase, eval = Eval(node, color, isendgame, 1, 2.5, 2.5, 4, 6)
        hash = chess.polyglot.zobrist_hash(node)
        if node.is_game_over():
            outcome = node.outcome().result()
            return drawval if "/" in outcome else (200 if outcome[0] == "1" else -200) * (1 if color else -1)
        if hash in game and game[hash] >= 1 + first:
            return drawval
        if istablebase:
            dtm = tablebase.probe_dtm(node)
            return drawval if dtm == 0 else dtm/abs(dtm)*200 * (1 if maximizingPlayer else -1)
        current = eval
        if depth == 0 or count >= 14:
            return current
        if not first and nodes[0] >= 15000:
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
                    drawcheck = hash in game and game[hash] >= 1
                    for move in list(fake.legal_moves):
                        child = fake.copy()
                        child.push(move)
                        childhash = chess.polyglot.zobrist_hash(child)
                        drawcheck = drawcheck or (childhash in game and game[childhash] >= 1)
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

    for i in range(1,10):
        start = time.time()
        move, val = alphabeta(board, i, -250, 250, True, True, 0)
        if move != None:
            bestmove = move
            bestval = val
        end = time.time()
        print("Depth %s: %s, value %s, %s nodes searched, %s seconds." % (i, bestmove, bestval, nodes[0], round(end-start,2)))
        if end - start > 1:
            return bestmove
    return bestmove

def Convert(n):
    alpha = ["a","b","c","d","e","f","g","h"]
    return alpha[n % 8]+ str(n // 8 + 1)

def Deconvert(s):
    dic = {"a":0,"b":1,"c":2,"d":3,"e":4,"f":5,"g":6,"h":7}
    return (int(s[1]) - 1) * 8 + dic[s[0]]

def Simulate(f1, f2):
    board = AntiBoard("8/8/4k3/8/8/3BBK2/8/8 w - - 0 1")
    turn = 0
    players = (f1,f2)
    while not board.is_game_over():
        print(board)
        print()
        move = players[turn](board)
        board.push_san(move)
        print("%s plays %s" % (["White","Black"][turn], move))
        turn = 1 - turn
    print("Outcome: " + str(board.outcome().result()))

def Human(board):
    print("Enter a move: ")
    print([str(m) for m in list(board.legal_moves)])
    move = input()
    while (move not in [str(m) for m in list(board.legal_moves)]):
        print("This is not a legal move, please enter one of the following legal moves: ")
        print([str(m) for m in list(board.legal_moves)])
        move = input()
    return move

whitetable = {}
blacktable = {}
board = AntiBoard("rr4n1/5pk1/6p1/6P1/6K1/8/5P2/5BQ1 w - - 0 1")
game = {}
#board.push_san(RandomMove(board))
#board.push_san(RandomMove(board))
while not board.is_game_over():
    board.push_san(God(board, 1, whitetable, -1.5))
    hash = chess.polyglot.zobrist_hash(board)
    try:
        game[hash] += 1
    except:
        game[hash] = 1
    print()
    board.push_san(God(board, 0, blacktable, -1.5))
    hash = chess.polyglot.zobrist_hash(board)
    try:
        game[hash] += 1
    except:
        game[hash] = 1
    print()

g = chess.pgn.Game()
for l in str(g.from_board(board)).split('\n'):
    print(l) 