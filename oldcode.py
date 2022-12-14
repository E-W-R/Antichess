def Test():
    choice = input("""
    1: Computer vs. Computer\n
    2: Computer vs. Human\n
    3: Human vs. Computer\n
    4: Human vs. Human\n\n
    Enter an option: """)
    
    if input("\nWould you like to give an initial board? (y/n): ") == "y":
        board = AntiBoard(input("Enter an FEN: "))
    else:
        board = AntiBoard()
    
    print()
    
    if choice == "1":
        color = 1
        while not board.outcome():
            print("%s plays %s" % (["Black","White"][color],RandomMove(board)))
            print(board)
            print()
            input("Press enter to continue\n")
            color = 1 - color
    
    if choice == "2":
        while not board.outcome():
            print("White plays %s" % RandomMove(board))
            print(board)
            print()
            key = True
            while key:
                try:
                    board.push_san(input("Enter a move: "))
                    key = False
                except:
                    print("Error, try again.")

    if choice == "3":
        while not board.outcome():
            key = True
            while key:
                try:
                    board.push_san(input("Enter a move: "))
                    key = False
                except:
                    print("Error, try again.")
            print("Black plays %s" % RandomMove(board))
            print(board)
            print()

    if choice == "4":
        color = 1
        while not board.outcome():
            key = True
            while key:
                try:
                    board.push_san(input("Enter a move for %s: " % ["black","white"][color]))
                    key = False
                except:
                    print("Error, try again.")
            print(board)
            print()
            color = 1 - color


def alphabeta(node, depth, alpha, beta, maximizingPlayer, first):
    if depth == 0:
        e1 = EvalBoard(node, 1, 3, 3, 5, 9)
        e2 = EvalBoardAttack(node)
        return (e1 + (e2[1] - e2[0]) * (abs(e1) < 8) * 0.05 + random.uniform(0,0.01)) * (1 if color else -1)
    if IsTablebase(node):
        dtm = tablebase.probe_dtm(node)
        return 0 if dtm == 0 else dtm/abs(dtm)*200
    if maximizingPlayer:
        value = -200
        for move in list(node.legal_moves):
            child = node.copy()
            child.push(move)
            v = alphabeta(child, depth - 1 + node.is_capture(move), alpha, beta, False, False)
            if v > value:
                value = v
                best = child
            if value >= beta: # make pruning constraints looser
                break
            alpha = max(alpha, value)
        return best if first else value
    else:
        value = 200
        for move in list(node.legal_moves):
            child = node.copy()
            child.push(move)
            v = alphabeta(child, depth - 1 + node.is_capture(move), alpha, beta, False, False)
            if v < value:
                value = v
                best = child
            if value <= alpha:
                break
            beta == min(beta, value)
        return best if first else value

def IsTablebase(board):
    whitepieces, blackpieces = 0, 0
    for i in range(64):
        piece = str(board.piece_at(i))
        whitepieces += piece.isupper()
        blackpieces += piece.islower()
    return (whitepieces == 1 and blackpieces <= 3) or (whitepieces <= 3 and blackpieces == 1)

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

def God(board, depth):
    nodes = [0]
    #vals = {"P":1,"N":3,"B":3,"R":5,"Q":9,"K":0}
    def alphabeta(node, depth, alpha, beta, maximizingPlayer, first):
        nodes[0] += 1
        capture = any(node.generate_legal_captures())
        istablebase, eval1, eval2 = Eval(node, 1, 3, 3, 5, 9)
        if istablebase:
            dtm = tablebase.probe_dtm(node)
            return 0 if dtm == 0 else dtm/abs(dtm)*200
        if depth == 0:
            return (eval1 + eval2 * (abs(eval1) < 5) * 0.05) * (1 if color else -1)
        #if any(node.generate_legal_captures()):
        #    return str(min(list(node.legal_moves), key = lambda m: vals[str(node.piece_at(Deconvert(str(m)[:2]))).upper()]))
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
                    if entry[0] == hash and (entry[1] >= depth or capture):
                        v = entry[2]
                    else:
                        v = alphabeta(child, depth - 1 + capture, alpha, beta, False, False)
                else:
                    v = alphabeta(child, depth - 1 + capture, alpha, beta, False, False)
                transtable[hash % tablesize] = [hash, depth - 1, v, 0]
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
                    if entry[0] == hash and (entry[1] >= depth or capture):
                        v = entry[2]
                    else:
                        v = alphabeta(child, depth - 1 + capture, alpha, beta, True, False)
                else:
                    v = alphabeta(child, depth - 1 + capture, alpha, beta, True, False)
                transtable[hash % tablesize] = [hash, depth - 1, v, 0]
                if v < value:
                    value = v
                    best = child
                value = min(value, v)
                if value <= alpha:
                    transtable[hash % tablesize][3] = -1
                    break
                beta == min(beta, value)
            return best if first else value
    
    #for i in range(1,depth-1):
    #    alphabeta(board, i, -200, 200, True, True)
    alphabeta(board, 1, -200, 200, True, True)
    return str(alphabeta(board, depth, -200, 200, True, True).pop()), nodes[0]

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