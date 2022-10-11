import sys
import chess
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

#board.legal_moves

while True:
    input()
    RandomMove()
    print(board)