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