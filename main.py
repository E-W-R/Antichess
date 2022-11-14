import sys
import chess
import chess.syzygy
import chess.gaviota
import random
import math

color = sys.argv[1]

class AntiBoard(chess.Board):
    @property
    def legal_moves(self):
        return MyLegalMoveGenerator(self)

class MyLegalMoveGenerator(chess.LegalMoveGenerator):
    def __iter__(self):
        return self.board.generate_legal_captures() if any(self.board.generate_legal_captures()) \
            else self.board.generate_legal_moves()

board = AntiBoard()

def RandomMove():
    moves = list(board.legal_moves)
    move = moves[random.randint(0,len(moves)-1)]
    board.push(moves[random.randint(0,len(moves)-1)])
    print(move)

tablebase = chess.gaviota.open_tablebase("tablebase")

def Endgame():
    while not board.is_checkmate():
        moves = list(board.legal_moves)
        n = abs(tablebase.probe_dtm(board))
        for move in moves:
            board.push(move)
            if (n == 1 and board.is_checkmate()) or \
            (n != 1 and abs(tablebase.probe_dtm(board)) == n - 1):
                print(move)
                break
            board.pop()
    board.push_san(input())

def EvalBoard(pawn, knight, bishop, rook, queen):
    dic = {'p' : (-1 * pawn), 'n' : (-1 * knight), 'b' : (-1 * bishop), 'r' : (-1 * rook), 'q' : (-1 * queen), 'k' : 0,
    'P' : pawn, 'N' : knight, 'B' : bishop, 'R' : rook, 'Q' : queen, 'K' : 0, 'None': 0}
    value = 0
    for i in range(64):
        piece =  str(board.piece_at(i))
        value += dic[piece]
    return value
        




