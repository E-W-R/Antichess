import sys
from turtle import color
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

board = AntiBoard()

def RandomMove(board):
    moves = list(board.legal_moves)
    move = moves[random.randint(0,len(moves)-1)]
    #board.push(moves[random.randint(0,len(moves)-1)])
    return(str(move))

tablebase = chess.gaviota.open_tablebase("tablebase")

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

def EvalBoard(pawn, knight, bishop, rook, queen):
    dic = {'p' : (-1 * pawn), 'n' : (-1 * knight), 'b' : (-1 * bishop), 'r' : (-1 * rook), 'q' : (-1 * queen), 'k' : 0,
    'P' : pawn, 'N' : knight, 'B' : bishop, 'R' : rook, 'Q' : queen, 'K' : 0, 'None': 0}
    value = 0
    for i in range(64):
        piece =  str(board.piece_at(i))
        value += dic[piece]
    return value

def Simulate(f1,f2):
    board = AntiBoard()
    turn = 0
    players = (f1,f2)
    while not board.outcome():
        print(board)
        move = players[turn](board)
        board.push_san(move)
        print("%s plays %s" % (["White","Black"][turn], move))
        print()
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