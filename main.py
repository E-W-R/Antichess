import sys
import chess
import chess.gaviota
import chess.polyglot
import random
import math
import time
import statistics

#color = int(sys.argv[1])
color = 1

class AntiBoard(chess.Board): 
    @property
    def legal_moves(self):
        return MyLegalMoveGenerator(self)

class MyLegalMoveGenerator(chess.LegalMoveGenerator):
    def __iter__(self):
        return self.board.generate_legal_captures() if any(self.board.generate_legal_captures()) \
            else self.board.generate_legal_moves()

board = AntiBoard()

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

def Eval(board, pawn, knight, bishop, rook, queen):
    wpieces, bpieces, value, attacks = 0, 0, 0, 0
    values = {'P' : pawn, 'N' : knight, 'B' : bishop, 'R' : rook, 'Q' : queen, 'K' : 0, 'NONE': 0}
    for i in range(64):
        piece = str(board.piece_at(i))
        wpieces += piece.isupper()
        bpieces += piece.islower()
        value += values[piece.upper()] * (1 if piece.isupper() else -1)
        attacks += len(board.attacks(i)) * (-1 if board.color_at(i) else 1)
    return ((wpieces == 1 and bpieces <= 3) or (wpieces <= 3 and bpieces == 1), value, attacks)

def Endgame(board):
    copyboard = board.copy()
    while not copyboard.is_game_over():
        moves = list(copyboard.legal_moves)
        n = abs(tablebase.probe_dtm(copyboard))
        for move in moves:
            if copyboard.is_capture(move):
                return str(move)
            copyboard.push(move)
            if (n == 1 and copyboard.is_checkmate()) or \
            (n != 1 and abs(tablebase.probe_dtm(copyboard)) == n - 1) or \
            (n == 0 and tablebase.probe_dtm(copyboard) == 0):
                return str(move)
            copyboard.pop()

tablesize = 2**16
transtable = {} # index: [hash, depth, value, flag, move]

def God(board):
    if len(list(board.legal_moves)) == 1:
        return str(list(board.legal_moves)[0])

    nodes = [0]
    def alphabeta(node, depth, alpha, beta, maximizingPlayer, first):
        nodes[0] += 1
        capture = any(node.generate_legal_captures())
        istablebase, eval1, eval2 = Eval(node, 1, 2, 2, 3, 4)
        if node.is_game_over():
            outcome = node.outcome().result()
            return -1 if "/" in outcome else (200 if outcome[0] == "1" else -200) * (1 if color else -1)
        if node.is_repetition():
            return -1
        if istablebase:
            dtm = tablebase.probe_dtm(node)
            return -1 if dtm == 0 else dtm/abs(dtm)*200 * (1 if maximizingPlayer else -1)
        current = (eval1 + eval2 * (abs(eval1) < 5) * 0.05) * (1 if color else -1)
        if depth == 0:
            return current
        hash = chess.polyglot.zobrist_hash(node)
        moves = list(node.legal_moves)
        if hash % tablesize in transtable:
            entry = transtable[hash % tablesize]
            if entry[0] == hash:
                moves = [chess.Move.from_uci(entry[4])] + moves
            if entry[0] == hash and entry[1] >= depth:
                if entry[3] == 0:
                    return entry[4] if first else entry[2]
                if entry[3] == 1 and entry[2] >= beta:
                    return entry[4] if first else entry[2]
                if entry[3] == -1 and entry[2] <= alpha:
                    return entry[4] if first else entry[2]

        if maximizingPlayer:
            if depth == 1 and current + 0.3 < alpha and (not capture):
                return current
            value = -300
            flag = -1
            for move in moves:
                child = node.copy()
                child.push(move)
                capturenext = any(child.generate_legal_captures())
                v = alphabeta(child, depth - 1 + capturenext, alpha, beta, False, False)
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
            return str(best) if first else value
        else:
            if depth == 1 and current - 0.3 > beta and (not capture):
                return current
            value = 300
            flag = 1
            for move in moves:
                child = node.copy()
                child.push(move)
                v = alphabeta(child, depth - 1 + capturenext, alpha, beta, True, False)
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
            return str(best) if first else value
    
    if IsTablebase(board):
        return Endgame(board)

    for i in range(1,5):
        start = time.time()
        move = alphabeta(board, i, -500, 500, True, True)
        print("Depth %s: %s with %s nodes searched." % (i, move, nodes[0]))
        end = time.time()
        if end - start > 0.5:
            return move
    return move

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

board = AntiBoard()
tablesize = 2**16
transtable = {}
color = 0
board.push_san(input())
while not board.is_game_over():
    move = God(board)
    board.push_san(move)
    print(move)
    board.push_san(input("Enter a move: "))
    print(board)
startingboard = AntiBoard()
print(startingboard.variation_san(board.move_stack))