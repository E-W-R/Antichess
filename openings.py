import chess
import chess.gaviota
import chess.polyglot

pawn = 1
knight = 2.5
bishop = 2.5
rook = 4
queen = 6
drawval = -1.2
maxdepth = 14

class AntiBoard(chess.Board): 
    @property
    def legal_moves(self):
        return MyLegalMoveGenerator(self)

class MyLegalMoveGenerator(chess.LegalMoveGenerator):
    def __iter__(self):
        return self.board.generate_legal_captures() if any(self.board.generate_legal_captures()) \
            else self.board.generate_legal_moves()

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
    return (istablebase, (value + attacks * 0.01) * (1 if color else -1))

tablesize = 2**16
transtable = {} # index: [hash, depth, value, flag, move]
game = {}

def alphabeta(node, depth, alpha, beta, maximizingPlayer, first, count):
    capture = any(node.generate_legal_captures())
    istablebase, eval = Eval(node, 0, False, 16, pawn, knight, bishop, rook, queen)
    hash = chess.polyglot.zobrist_hash(node)
    if hash in game and not first:
        return drawval
    if node.is_game_over():
        outcome = node.outcome().result()
        return drawval if "/" in outcome else (200 if outcome[0] == "1" else -200) * (1 if 0 else -1)
    if hash in game and not first:
        return drawval
    if istablebase:
        dtm = tablebase.probe_dtm(node)
        return drawval if dtm == 0 else dtm/abs(dtm)*200 * (1 if maximizingPlayer else -1)
    current = eval
    if depth == 0 or count >= maxdepth:
        return current
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
            v = alphabeta(child, depth - 1 + capturenext, alpha, beta, False, False, count + 1)
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

board = AntiBoard()
f = open('4.txt', 'w')
for move1 in list(board.legal_moves):
    board.push(move1)
    for move2 in list(board.legal_moves):
        board.push(move2)
        for move3 in list(board.legal_moves):
            board.push(move3)
            s = str(chess.polyglot.zobrist_hash(board)) + ':' + alphabeta(board, 4, -250, 250, True, True, 0)[0]
            print(s)
            f.write(s + '\n')
            board.pop()
        board.pop()
    board.pop()
f.close()