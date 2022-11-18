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