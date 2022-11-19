import sys
import time
import statistics
#from turtle import color
import chess
import chess.gaviota
import random
import math
import time

#color = int(sys.argv[1])

class AntiBoard(chess.Board): 
    @property
    def legal_moves(self):
        return MyLegalMoveGenerator(self)

class MyLegalMoveGenerator(chess.LegalMoveGenerator):
    def __iter__(self):
        return self.board.generate_legal_captures() if any(self.board.generate_legal_captures()) \
            else self.board.generate_legal_moves()

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

def alphabeta(node, depth, alpha, beta, maximizingPlayer):
    if depth == 0 or node.outcome():
        return EvalBoard(node, 1, 3, 3, 5, 9) #+ EvalBoardAttack(node)
    if maximizingPlayer:
        value = -200
        for move in list(node.legal_moves):
            child = node.copy()
            child.push(move)
            value = max(value, alphabeta(child, depth - 1, alpha, beta, False))
            if value >= beta:
                break
            alpha = max(alpha, value)
        return value
    else:
        value = 200
        for move in list(node.legal_moves):
            child = node.copy()
            child.push(move)
            value = min(value, alphabeta(child, depth - 1, alpha, beta, True))
            if value <= alpha:
                break
            beta == min(beta, value)
        return value

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



#Simulate(RandomMove,RandomMove)

def ComputerL1(board):
    dic = {'p' : 0, 'n' : 0, 'b' : 0, 'r' : 0, 'q' : 0, 'k' : 0,
    'P' : 0, 'N' : 0, 'B' : 0, 'R' : 0, 'Q' : 0, 'K' : 0, 'None': 0}
    piece = 0
    for i in range(64):
        piece =  str(board.piece_at(i))
        value += dic[piece]
    return value
    moves = list(board.legal_moves)
    move = moves[random.randint(0,len(moves)-1)]
    #board.push(moves[random.randint(0,len(moves)-1)])
    return(str(move))

def EvalBoardattack(board):
    white = 0
    black = 0
    for i in range(64):
        if (board.color_at(i) == True):
            white += len(board.attacks(i))
        elif(board.color_at(i) == False):
            black += len(board.attacks(i))
    return [white, black]

def Convert(n):
    alpha = ["a","b","c","d","e","f","g","h"]
    return alpha[n % 8]+ str(n // 8 + 1)

#print(Convert(5))

board = AntiBoard()
#print(Convert(1))
#print(board.color_at(40))
#print(EvalBoardattack(board))

def Sack(board, colour):
    dic = {'p' : [], 'n' : [], 'b' : [], 'r' : [], 'q' : [], 'k' : [],
    'P' : [], 'N' : [], 'B' : [], 'R' : [], 'Q' : [], 'K' : []}
    piece = 0
    for i in range(64):
        piece =  str(board.piece_at(i))
        if piece != 'None':
            dic[piece].append(i)
    if (colour):
        if (dic['Q'] != []):
            if (dic['R'] != []):
                move = SackPiece(board, dic['R'][0], dic['k'][0])
                return Convert(move[0]) + Convert(move[1])
            elif (dic['B'] != []):
                move = SackPiece(board, dic['R'][0], dic['k'][0])
                return Convert(move[0]) + Convert(move[1])
            elif (dic['N'] != []):
                move = SackPiece(board, dic['R'][0], dic['k'][0])
                return Convert(move[0]) + Convert(move[1])
        elif (dic['R'] != []):
            if (dic['B'] != []):
                move = SackPiece(board, dic['R'][0], dic['k'][0])
                return Convert(move[0]) + Convert(move[1])
            elif (dic['N'] != []):
                move = SackPiece(board, dic['R'][0], dic['k'][0])
                return Convert(move[0]) + Convert(move[1])
        elif (len(dic['B']) >= 2):
            if (dic['B'] != []):
                move = SackPiece(board, dic['R'][0], dic['k'][0])
                return Convert(move[0]) + Convert(move[1])
        elif (len(dic['N']) >= 2):
            print(1)
        elif (len(dic['N'] + len(dic['B'])) >= 2):
            print(1)
            #sack everything else
        else:
            print(5)

    return "A"

def Distance(s1 , s2):
    dist = abs(s1-s2)
    return dist % 8 + dist // 8

def SackPiece(board, s1, s2):
    #dic = {'p' : [], 'n' : [], 'b' : [], 'r' : [], 'q' : [], 'k' : [],
    #'P' : [], 'N' : [], 'B' : [], 'R' : [], 'Q' : [], 'K' : []}
    #print(s1, s2)
    poss = board.attacks(s1)
    #print(poss)
    min = 100
    for move in poss:
        dist = Distance(move, s2)
        #print(dist)
        if (dist < min):
            min = dist
    for move in poss:
        dist = Distance(move, s2)
        if (dist == min):
            return (s1, move)


def SimulateN(f1, f2, n):
    ww = 0
    bw = 0
    wtimes = []
    btimes = []
    for i in range(n):
        board = AntiBoard()
        turn = 0
        players = (f1,f2)
        wtime = 0
        btime = 0
        while not board.outcome():
            #print(i)
            #print(board)
            #print()
            start = time.time()
            move = players[turn](board)
            end = time.time()
            if (turn == 0):
                wtime += (end - start)
            elif (turn == 1):
                btime += (end - start)
            board.push_san(move)
            #print("%s plays %s" % (["White","Black"][turn], move))
            turn = 1 - turn
        wtimes.append(wtime)
        btimes.append(btime)
        #print(str(board.outcome().result()))
        if (str(board.outcome().result()) == "1/2-1/2"):
            ww += 0.5
            bw += 0.5
        else: 
            ww += int(str(board.outcome().result())[0])
            bw += int(str(board.outcome().result())[2])
    print(ww, bw, statistics.mean(wtimes), statistics.mean(btimes))


#SimulateN(RandomMove,RandomMove, 100)

#print(time.time())
#print(time.process_time())
#print(time.process_time())

print(Sack(AntiBoard("7k/8/8/8/8/8/1R6/KQ6 w - - 0 1"), True))