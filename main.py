import sys
from turtle import color
import chess
import chess.gaviota
#import chess.svg
import random

#colour = sys.argv[1]

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

## Call this function on our turn once we have 4 or fewer pieces and the opponent has none
def Endgame():
    with chess.gaviota.open_tablebase("data/gaviota") as tablebase:
        while not chess.Board.is_checkmate():
            turns_left = tablebase.probe_dtm(board)
            for move in list(board.legal_moves):
                board.push(move)
                if tablebase.probe_dtm(board) < turns_left:
                    break
                else:
                    board.pop()
            board.push_san(input())

#board.legal_moves

if color == "white":
    RandomMove()

while True:
    board.push_san(input())
    RandomMove()

#while True:
#    input()
#    RandomMove()
#    print(board)