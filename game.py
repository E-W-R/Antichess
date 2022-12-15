from subprocess import Popen, PIPE
import chess
import chess.pgn
import time
import sys

f1, f2 =  sys.argv[1], sys.argv[2]
fs = [f1, f2]
p1times, p2times = [], []
times = [p1times, p2times]
p1w, p2w = 0, 0
pws = [p1w, p2w]
PGNs = []

def sim(n):
    for i in range(n):
        p1, p2 = i%2, (i+1)%2

        board = chess.Board()
        script1 = Popen(["pypy3", fs[p1], "white"], stdin=PIPE, stdout=PIPE)
        script2 = Popen(["pypy3", fs[p2], "black"], stdin=PIPE, stdout=PIPE)
        print()

        t1, t2 = 180, 180
        start = time.time()
        while not board.is_game_over() and t1 > 0 and t2 > 0:
            output1 = script1.stdout.readline()
            if output1.decode('ascii') in ['', 'End']:   break
            board.push_san(output1.decode('ascii')[:-1])
            print(output1.decode('ascii'))
            script2.stdin.write(output1)
            script2.stdin.flush()
            end = time.time()
            t1 -= end - start
            start = end

            if board.is_game_over():
                break

            output2 = script2.stdout.readline()
            if output2.decode('ascii') in ['', 'End']:   break
            board.push_san(output2.decode('ascii')[:-1])
            print(output2.decode('ascii'))
            script1.stdin.write(output2)
            script1.stdin.flush()
            end = time.time()
            t2 -= end - start
            start = end

        script1.terminate()
        script2.terminate()

        times[p1].append(t1)
        times[p2].append(t2)
        if not board.is_game_over():
            pws[p1] += t1 > 0
            pws[p2] += t2 > 0
        if (str(board.outcome().result()) == "1/2-1/2"):
            pws[p1] += 0.5
            pws[p2] += 0.5
        else: 
            pws[p1] += int(str(board.outcome().result())[0])
            pws[p2] += int(str(board.outcome().result())[2])
        print(t1, t2, str(board.outcome().result()))
        g = chess.pgn.Game()
        PGNs.append(str(g.from_board(board)).split('\n')[-1])
    
    print(pws, times, PGNs)

sim(2)