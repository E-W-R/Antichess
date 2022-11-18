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

board = AntiBoard("r1bqkb1r/1p1ppppp/2n2n2/p1p5/P1P5/3P4/1PQ1PPPP/RNB1KBNR w KQkq - 3 5")

def RandomMove(board):
    if IsTablebase(board):
        return Endgame(board)
    moves = list(board.legal_moves)
    move = moves[random.randint(0,len(moves)-1)]
    #board.push(moves[random.randint(0,len(moves)-1)])
    return(str(move))

tablebase = chess.gaviota.open_tablebase("tablebase")

def IsTablebase(board):
    whitepieces, blackpieces = 0, 0
    for i in range(64):
        piece = str(board.piece_at(i))
        whitepieces += piece.isupper()
        blackpieces += piece.islower()
    return (whitepieces == 1 and blackpieces <= 3) or (whitepieces <= 3 and blackpieces == 1)

def Endgame(board):
    copyboard = board.copy()
    while not copyboard.outcome():
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

def EvalBoard(board, pawn, knight, bishop, rook, queen):
    dic = {'p' : (-1 * pawn), 'n' : (-1 * knight), 'b' : (-1 * bishop), 'r' : (-1 * rook), 'q' : (-1 * queen), 'k' : 0,
    'P' : pawn, 'N' : knight, 'B' : bishop, 'R' : rook, 'Q' : queen, 'K' : 0, 'None': 0}
    value = 0
    for i in range(64):
        piece = str(board.piece_at(i))
        value += dic[piece]
    return value

def EvalBoardAttack(board):
    white = 0
    black = 0
    for i in range(64):
        if (board.color_at(i) == True):
            white += len(board.attacks(i))
        elif(board.color_at(i) == False):
            black += len(board.attacks(i))
    return [white, black]

tablesize = 2**12
transtable = {} # index: [hash, depth, value, flag] 2x

def God(board, depth): # Implements Alpha-Beta pruning, Iterative deepening, Transposition tables, Killer heuristic, and Tablebases

    def alphabeta(node, depth, alpha, beta, maximizingPlayer, first):
        if IsTablebase(node):
            dtm = tablebase.probe_dtm(node)
            return 0 if dtm == 0 else dtm/abs(dtm)*200
        if depth == 0:
            e1 = EvalBoard(node, 1, 3, 3, 5, 9)
            e2 = EvalBoardAttack(node)
            return (e1 + (e2[1] - e2[0]) * (abs(e1) < 8) * 0.05 + random.uniform(0,0.01)) * (1 if color else -1)
        children = []
        for move in list(node.legal_moves):
            child = node.copy()
            child.push(move)
            children.append(child)
        def priority(child):
            hash = chess.polyglot.zobrist_hash(child)
            if hash % tablesize in transtable:
                entry = transtable[hash % tablesize]
                if entry[0] == hash:
                    return (entry[3], entry[2])
            return (0, 0)
        children.sort(key = priority, reverse = maximizingPlayer)
        if maximizingPlayer:
            value = -200
            for child in children:
                hash = chess.polyglot.zobrist_hash(child)
                if hash % tablesize in transtable:
                    entry = transtable[hash % tablesize]
                    if entry[0] == hash and entry[1] >= depth:
                        v = entry[2]
                    else:
                        v = alphabeta(child, depth - 1 + node.is_capture(move), alpha, beta, False, False)
                else:
                    v = alphabeta(child, depth - 1 + node.is_capture(move), alpha, beta, False, False)
                transtable[hash % tablesize] = [hash, depth, v, 0]
                if v > value:
                    value = v
                    best = child
                if value >= beta:
                    transtable[hash % tablesize][3] = 1
                    break
                alpha = max(alpha, value)
            return best if first else value
        else:
            value = 200
            for child in children:
                hash = chess.polyglot.zobrist_hash(child)
                if hash % tablesize in transtable:
                    entry = transtable[hash % tablesize]
                    if entry[0] == hash and entry[1] >= depth:
                        v = entry[2]
                    else:
                        v = alphabeta(child, depth - 1 + node.is_capture(move), alpha, beta, True, False)
                else:
                    v = alphabeta(child, depth - 1 + node.is_capture(move), alpha, beta, True, False)
                transtable[hash % tablesize] = [hash, depth, v, 0]
                if v < value:
                    value = v
                    best = child
                value = min(value, v)
                if value <= alpha:
                    transtable[hash % tablesize][3] = -1
                    break
                beta == min(beta, value)
            return best if first else value
    
    alphabeta(board, 1, -200, 200, True, True)
    return str(alphabeta(board, depth, -200, 200, True, True).pop())

def Convert(n):
    alpha = ["a","b","c","d","e","f","g","h"]
    return alpha[n % 8]+ str(n // 8 + 1)

def Simulate(f1, f2):
    board = AntiBoard("8/8/4k3/8/8/3BBK2/8/8 w - - 0 1")
    turn = 0
    players = (f1,f2)
    while not board.outcome():
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



Simulate(Human,RandomMove)