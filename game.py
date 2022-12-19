from subprocess import Popen, PIPE
import chess
import chess.pgn
import time
import sys

f1, f2 =  sys.argv[1], sys.argv[2]
f = open('%s v %s.txt' % (f1, f2), 'w')
print()

def sim(n):
    for i in range(n):
        s = "Game %s, %s v %s:" % (i + 1, [f1,f2][i%2], [f1,f2][(i+1)%2])
        print(s)
        f.write(s + '\n')

        board = chess.Board()
        script1 = Popen(["pypy3", [f1,f2][i%2], "white"], stdin=PIPE, stdout=PIPE)
        script2 = Popen(["pypy3", [f1,f2][(i+1)%2], "black"], stdin=PIPE, stdout=PIPE)

        t1, t2 = 0, 0
        start = time.time()
        while not board.is_game_over() and t1 < 180 and t2 < 180:
            output1 = script1.stdout.readline()
            if output1.decode('ascii') in ['', 'End']:   break
            board.push_san(output1.decode('ascii')[:-1])
            #print(output1.decode('ascii'))
            script2.stdin.write(output1)
            script2.stdin.flush()
            end = time.time()
            t1 += end - start
            start = end

            if board.is_game_over():
                break

            output2 = script2.stdout.readline()
            if output2.decode('ascii') in ['', 'End']:   break
            board.push_san(output2.decode('ascii')[:-1])
            #print(output2.decode('ascii'))
            script1.stdin.write(output2)
            script1.stdin.flush()
            end = time.time()
            t2 += end - start
            start = end

        script1.terminate()
        script2.terminate()

        if board.is_game_over():
            if (str(board.outcome().result()) == "1/2-1/2"):
                s = "Draw, P1: %s:%s, P2: %s:%s" % (int(t1//60),round(t1%60),int(t1//60),round(t1%60))
            else:
                winner = 2 - int(str(board.outcome().result())[0])
                s = "Player %s wins, P1: %s:%s, P2: %s:%s" % (winner,int(t1//60),round(t1%60),int(t2//60),round(t2%60))
        else:
            s = "Player %s wins, P1: %s:%s, P2: %s:%s" % (1 + (t2 > 0),int(t1//60),round(t1%60),int(t2//60),round(t2%60))
        print(s)
        f.write(s + '\n')
        pgn = str(chess.pgn.Game().from_board(board)).split('\n')[-1] + '\n'
        print(pgn)
        f.write(pgn + '\n')

    f.close()

sim(2)